"""
Article summarizer for generating concise summaries
"""
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import config

class ArticleSummarizer:
    def __init__(self, llm_model=None):
        model_name = llm_model or config.OPENAI_MODEL
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0.5,
            model=model_name
        )
        
        # Create prompt template for summarization
        self.summarize_prompt = PromptTemplate(
            input_variables=["article_title", "article_content", "article_category"],
            template="""
            You are an AI assistant tasked with summarizing articles.
            
            Article Title: {article_title}
            
            Article Content: {article_content}
            
            Article Category: {article_category}
            
            Create a concise one-paragraph summary of this article that captures the key insights.
            Focus on the most important information, especially as it relates to the article's category.
            The summary should be informative, clear, and around 3-5 sentences.
            Do not use phrases like "this article" or "the author states" - just present the information directly.
            """
        )
        
        # Create LLMChain for summarization
        self.summarize_chain = LLMChain(
            llm=self.llm,
            prompt=self.summarize_prompt
        )
    
    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a concise summary for an article
        """
        # Prepare content for summarization
        article_title = article.get('title', '')
        article_content = article.get('content', article.get('summary', ''))
        article_category = article.get('category', 'GENERAL')
        
        # Truncate content to avoid token limits
        max_content_length = 3000
        if len(article_content) > max_content_length:
            article_content = article_content[:max_content_length] + "..."
        
        # Run summarization
        try:
            response = self.summarize_chain.invoke({
                "article_title": article_title,
                "article_content": article_content,
                "article_category": article_category
            })
            
            # Add summary to article
            article['ai_summary'] = response['text'].strip()
            return article
            
        except Exception as e:
            print(f"Error summarizing article: {str(e)}")
            # Default summary in case of error
            article['ai_summary'] = f"Failed to generate summary for '{article_title}'."
            return article
    
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize a list of articles
        """
        summarized_articles = []
        
        for article in articles:
            summarized_article = self.summarize_article(article)
            summarized_articles.append(summarized_article)
            print(f"Summarized '{article.get('title', 'Untitled')}'")
        
        return summarized_articles

if __name__ == "__main__":
    # Simple test
    import os
    from fetcher import RSSFetcher
    from filter import ArticleFilter
    from categorizer import ArticleCategorizer
    
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Fetch, filter, and categorize some articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    
    if not articles:
        print("No articles fetched. Cannot test summarization.")
        exit(1)
    
    # Filter articles
    article_filter = ArticleFilter()
    relevant_articles = article_filter.filter_articles(articles[:2])
    
    if not relevant_articles:
        print("No relevant articles found. Cannot test summarization.")
        exit(1)
    
    # Categorize articles
    categorizer = ArticleCategorizer()
    categorized_articles = categorizer.categorize_articles(relevant_articles)
    
    # Summarize articles
    summarizer = ArticleSummarizer()
    summarized_articles = summarizer.summarize_articles(categorized_articles)
    
    # Print results
    for article in summarized_articles:
        print(f"\n{article.get('category_emoji', '')} {article.get('title', 'Untitled')}")
        print(f"Summary: {article.get('ai_summary', 'No summary generated.')}") 