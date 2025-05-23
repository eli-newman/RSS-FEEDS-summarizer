"""
Article filter for relevance using LangChain
"""
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import config
import os

class ArticleFilter:
    def __init__(self, topics=None, llm_model=None):
        self.topics = topics or config.TOPICS_OF_INTEREST
        model_name = llm_model or config.OPENAI_MODEL
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0.1,
            model=model_name
        )
        
        # Create prompt template for relevance checking
        self.relevance_prompt = PromptTemplate(
            input_variables=["article_title", "article_content", "topics"],
            template="""
            You are an AI assistant tasked with filtering articles for relevance.
            
            Article Title: {article_title}
            
            Article Content: {article_content}
            
            Topics of Interest: {topics}
            
            Is this article relevant to any of the topics of interest? 
            Respond with only "YES" or "NO".
            """
        )
        
        # Create LLMChain for relevance checking
        self.relevance_chain = LLMChain(
            llm=self.llm,
            prompt=self.relevance_prompt
        )
    
    def is_article_relevant(self, article: Dict[str, Any]) -> bool:
        """
        Check if an article is relevant to the topics of interest
        """
        # Prepare content for analysis
        article_title = article.get('title', '')
        article_content = article.get('content', article.get('summary', ''))
        
        # Truncate content to avoid token limits
        max_content_length = 1000
        if len(article_content) > max_content_length:
            article_content = article_content[:max_content_length] + "..."
        
        # Run relevance check
        try:
            response = self.relevance_chain.invoke({
                "article_title": article_title,
                "article_content": article_content,
                "topics": ", ".join(self.topics)
            })
            
            # Check if response contains YES
            return "YES" in response['text'].upper()
        
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            # Default to True in case of error to avoid missing potentially relevant articles
            return True
    
    def filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of articles by relevance
        """
        relevant_articles = []
        
        for article in articles:
            if self.is_article_relevant(article):
                relevant_articles.append(article)
        
        return relevant_articles

if __name__ == "__main__":
    # Simple test (requires OPENAI_API_KEY environment variable)
    from fetcher import RSSFetcher
    
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Fetch some articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    
    if not articles:
        print("No articles fetched. Cannot test filtering.")
        exit(1)
    
    # Filter articles
    filter = ArticleFilter()
    relevant_articles = filter.filter_articles(articles[:3])  # Test with first 3 articles
    
    print(f"Filtered {len(relevant_articles)} relevant articles out of 3 tested") 