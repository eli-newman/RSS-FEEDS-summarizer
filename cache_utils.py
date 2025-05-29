"""
Shared cache utilities for the RSS summarizer
"""

class CacheTracker:
    def __init__(self, cost_per_call=0.01):
        self.cache_hits = 0
        self.cache_misses = 0
        self.cost_per_call = cost_per_call
        self.estimated_savings = 0
    
    def record_hit(self):
        self.cache_hits += 1
        self.estimated_savings += self.cost_per_call
    
    def record_miss(self):
        self.cache_misses += 1
    
    def get_stats(self):
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'estimated_savings': f"${self.estimated_savings:.2f}"
        } 