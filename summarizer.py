"""
AI-powered article summarizer
"""
import os
import time
from typing import List, Dict, Any
from openai import OpenAI
from tqdm import tqdm
import config

class ArticleSummarizer:
    def __init__(self, api_key=None, model=None):
        """
        Initialize the summarizer with OpenAI credentials
        
        Args:
            api_key: OpenAI API key (defaults to config.OPENAI_API_KEY)
            model: OpenAI model to use for summarization
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model or config.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key)
    
    def preselect_product_hunt_tools(self, tools: List[Dict[str, Any]], max_tools: int = 3) -> List[Dict[str, Any]]:
        """
        Pre-select the most promising Product Hunt tools before full summarization
        This is more cost-efficient than summarizing all tools first
        
        Args:
            tools: List of Product Hunt tool articles
            max_tools: Maximum number of tools to select
            
        Returns:
            List of selected tool articles
        """
        if not tools:
            return []
            
        if len(tools) <= max_tools:
            return tools
            
        print(f"Pre-selecting top {max_tools} tools from {len(tools)} Product Hunt tools...")
        
        # Extract basic info from each tool
        tool_info = []
        for tool in tools:
            title = tool.get('title', 'No Title')
            description = tool.get('summary', '')
            if not description and 'content' in tool:
                # Extract a short description from content if available
                content = tool.get('content', '')
                description = content[:200] + "..." if len(content) > 200 else content
                
            tool_info.append({
                "title": title,
                "description": description
            })
        
        try:
            # Create a simple prompt to select the most promising tools
            prompt = f"""Based only on the titles and descriptions, select the {max_tools} most innovative and useful AI tools from this list of Product Hunt submissions.
            
            Consider:
            1. Usefulness and practical applications
            2. Innovation and uniqueness
            3. Technical impressiveness
            
            Tools:
            {tool_info}
            
            Return ONLY a JSON array with the titles of the top {max_tools} tools, like this:
            ["Tool Title 1", "Tool Title 2", "Tool Title 3"]
            
            Do not include any explanation or other text.
            """
            
            # Use a small model (e.g., gpt-3.5-turbo) to save costs
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a smaller model to reduce costs
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating AI tools based on limited information. Your job is to select the most promising tools from a list."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3  # Low temperature for consistent selection
            )
            
            # Parse the response
            import json
            try:
                response_text = response.choices[0].message.content.strip()
                # Try to extract JSON if it's wrapped in backticks or other text
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                selected_titles = json.loads(response_text)
                
                # Match the selected titles with the original tool objects
                selected_tools = []
                for title in selected_titles:
                    # Find the tool with this title
                    matching_tools = [t for t in tools if title.lower() in t.get('title', '').lower()]
                    if matching_tools:
                        selected_tools.append(matching_tools[0])
                
                # If we couldn't match all tools, fill the rest based on order
                if len(selected_tools) < max_tools:
                    remaining_tools = [t for t in tools if t not in selected_tools]
                    selected_tools.extend(remaining_tools[:max_tools - len(selected_tools)])
                
                print(f"Selected {len(selected_tools)} tools for detailed summarization")
                return selected_tools
                
            except json.JSONDecodeError:
                print("Error parsing JSON response from preselection")
                print(f"Response content: {response.choices[0].message.content}")
                # Fallback to first max_tools
                return tools[:max_tools]
            
        except Exception as e:
            print(f"Error preselecting tools: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback to first max_tools
            return tools[:max_tools]
    
    def summarize_article(self, article: Dict[str, Any]) -> str:
        """
        Generate a concise 2-sentence summary of an article
        
        Args:
            article: Article dictionary containing title, content, etc.
            
        Returns:
            Concise AI-generated summary
        """
        # Combine title and content
        title = article.get('title', '')
        content = article.get('content', article.get('summary', ''))
        
        # Limit content length to avoid excessive token usage
        if len(content) > 8000:
            content = content[:8000] + "..."
        
        try:
            # Create prompt for summarization
            prompt = f"""Summarize the following article in EXACTLY 2 sentences. 
            The first sentence should capture the most important point.
            The second sentence should provide the most critical detail or implication.
            Be direct and informative. less is more. 
            
            Title: {title}
            
            Content: {content}
            
            Two-sentence summary:"""
            
            # Generate summary using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries of technical articles in exactly 2 sentences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3  # Low temperature for more focused summary
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error summarizing article '{title}': {str(e)}")
            # Return original summary if available, otherwise a snippet of content
            return article.get('summary', content[:200] + "...")
    
    def rank_product_hunt_tools(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze and rank Product Hunt tools based on usefulness and innovation
        
        Args:
            articles: List of article dictionaries (from Product Hunt)
            
        Returns:
            List of ranked articles with added 'tool_rank' and 'tool_score' fields
        """
        # Filter only Product Hunt articles
        product_hunt_articles = [a for a in articles if "Product Hunt" in a.get('source', '')]
        
        if not product_hunt_articles:
            return articles
        
        print(f"Ranking {len(product_hunt_articles)} Product Hunt tools...")
        
        # Prepare data for batch analysis
        tool_data = []
        for article in product_hunt_articles:
            title = article.get('title', '')
            summary = article.get('ai_summary', article.get('summary', ''))
            tool_data.append({"title": title, "summary": summary})
        
        try:
            # Create prompt for ranking
            prompt = f"""Analyze these Product Hunt tools and rate each on a scale of 1-10 based on:
            1. Innovation (how novel and unique the tool is)
            2. Usefulness (practical value to users)
            3. Technical impressiveness
            
            Return a JSON array with each tool having:
            1. title: The tool name
            2. score: Overall score (1-10)
            3. reasoning: Brief explanation of the score
            
            Tools to analyze:
            {tool_data}
            
            Respond with only the JSON data in this format:
            [
                {{
                    "title": "Tool Name",
                    "score": 8.5,
                    "reasoning": "Brief explanation"
                }},
                ...
            ]
            """
            
            # Generate ranking using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating AI tools and products. You provide objective, insightful rankings based on innovation, usefulness, and technical merit. Your response should be in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2  # Low temperature for consistent ranking
            )
            
            # Parse the response
            import json
            try:
                response_text = response.choices[0].message.content.strip()
                # Try to extract JSON if it's wrapped in backticks or other text
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                ranking_data = json.loads(response_text)
                if isinstance(ranking_data, dict) and "tools" in ranking_data:
                    rankings = ranking_data["tools"]
                elif isinstance(ranking_data, list):
                    rankings = ranking_data
                else:
                    rankings = []
                    print("Unexpected format in ranking response")
            except json.JSONDecodeError:
                print("Error parsing JSON response from ranking")
                print(f"Response content: {response.choices[0].message.content}")
                rankings = []
            
            # Create a lookup of scores by title
            scores_by_title = {r.get('title', ''): (r.get('score', 0), r.get('reasoning', '')) for r in rankings}
            
            # Add scores to original articles
            for article in product_hunt_articles:
                title = article.get('title', '')
                score_data = scores_by_title.get(title, (0, ""))
                article['tool_score'] = score_data[0]
                article['tool_reasoning'] = score_data[1]
            
            # Sort by score
            ranked_articles = sorted(product_hunt_articles, key=lambda x: x.get('tool_score', 0), reverse=True)
            
            print(f"Ranked {len(ranked_articles)} Product Hunt tools")
            return ranked_articles
            
        except Exception as e:
            print(f"Error ranking Product Hunt tools: {str(e)}")
            import traceback
            traceback.print_exc()
            return product_hunt_articles
    
    def batch_summarize(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize a batch of articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of articles with added AI summaries
        """
        summarized_articles = []
        
        print(f"Generating AI summaries for {len(articles)} articles...")
        for article in tqdm(articles):
            # Generate summary for all articles
            ai_summary = self.summarize_article(article)
            
            # Add summary to article, replacing the original summary
            article_copy = article.copy()
            article_copy['ai_summary'] = ai_summary
            article_copy['summary'] = ai_summary  # Replace original summary
            summarized_articles.append(article_copy)
            
            # Brief pause to avoid rate limits
            time.sleep(0.5)
            
        return summarized_articles

if __name__ == "__main__":
    # Test the summarizer on a few articles
    from fetcher import RSSFetcher
    import filter
    
    # Fetch and filter articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    filtered_articles = filter.filter_articles(articles)
    
    # Summarize a few articles for testing
    summarizer = ArticleSummarizer()
    summarized = summarizer.batch_summarize(filtered_articles[:3])  # Just test with 3 articles
    
    # Display results
    for i, article in enumerate(summarized):
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"Original length: {len(article.get('content', ''))}")
        print(f"AI Summary: {article['ai_summary']}") 