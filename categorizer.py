"""
Article categorizer to assign topics/tags to relevant articles
"""
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import config
import json

class ArticleCategorizer:
    def __init__(self, categories=None, llm_model=None):
        self.categories = categories or config.CATEGORIES
        model_name = llm_model or config.OPENAI_MODEL
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0.3,
            model=model_name
        )
        
        # Create prompt template for categorization
        category_list = ", ".join([f"{emoji} {name}" for name, emoji in self.categories.items()])
        
        self.categorize_prompt = PromptTemplate(
            input_variables=["article_title", "article_content", "categories"],
            template="""
            You are an AI assistant tasked with categorizing articles.
            
            Article Title: {article_title}
            
            Article Content: {article_content}
            
            Available Categories: {categories}
            
            Analyze the article and assign the most appropriate category from the list above.
            Respond with only the category name. If none fit, respond with "OTHER".
            """
        )
        
        # Create LLMChain for categorization
        self.categorize_chain = LLMChain(
            llm=self.llm,
            prompt=self.categorize_prompt
        )
    
    def categorize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign a category to an article
        """
        # Prepare content for analysis
        article_title = article.get('title', '')
        article_content = article.get('content', article.get('summary', ''))
        
        # Truncate content to avoid token limits
        max_content_length = 1000
        if len(article_content) > max_content_length:
            article_content = article_content[:max_content_length] + "..."
        
        # Format categories for prompt
        categories_formatted = ", ".join([f"{cat} ({emoji})" for cat, emoji in self.categories.items()])
        
        # Run categorization
        try:
            response = self.categorize_chain.invoke({
                "article_title": article_title,
                "article_content": article_content,
                "categories": categories_formatted
            })
            
            # Extract category from response
            category_text = response['text'].strip().upper()
            
            # Find matching category
            assigned_category = "OTHER"
            for category in self.categories.keys():
                if category in category_text:
                    assigned_category = category
                    break
            
            # Add category and emoji to article
            article['category'] = assigned_category
            article['category_emoji'] = self.categories.get(assigned_category, "")
            
            return article
            
        except Exception as e:
            print(f"Error categorizing article: {str(e)}")
            # Default category in case of error
            article['category'] = "OTHER"
            article['category_emoji'] = ""
            return article
    
    def categorize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize a list of articles
        """
        categorized_articles = []
        
        for article in articles:
            categorized_article = self.categorize_article(article)
            categorized_articles.append(categorized_article)
            print(f"Categorized '{article.get('title', 'Untitled')}' as {categorized_article.get('category', 'OTHER')}")
        
        return categorized_articles

if __name__ == "__main__":
    # Simple test
    import os
    from fetcher import RSSFetcher
    from filter import ArticleFilter
    
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Fetch and filter some articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    
    if not articles:
        print("No articles fetched. Cannot test categorization.")
        exit(1)
    
    # Filter articles
    article_filter = ArticleFilter()
    relevant_articles = article_filter.filter_articles(articles[:3])
    
    if not relevant_articles:
        print("No relevant articles found. Cannot test categorization.")
        exit(1)
    
    # Categorize articles
    categorizer = ArticleCategorizer()
    categorized_articles = categorizer.categorize_articles(relevant_articles)
    
    # Print results
    for article in categorized_articles:
        print(f"\n{article.get('category_emoji', '')} {article.get('title', 'Untitled')} - {article.get('category', 'OTHER')}") 