mock_research = {
    "Apple Inc.": {
        "recent_news": "Launched Vision Pro, expanding services revenue",
        "stock_info": "Trading at $195, up 45% YTD",
        "key_developments": "AI integration across product line"
    },
    "Apple": {
        "recent_news": "Launched Vision Pro, expanding services revenue",
        "stock_info": "Trading at $195, up 45% YTD",
        "key_developments": "AI integration across product line"
    },
    "Tesla": {
        "recent_news": "Cybertruck deliveries ramping up",
        "stock_info": "Trading at $242, volatile quarter",
        "key_developments": "FSD v12 rollout, energy storage growth"
    },
    "Tesla Inc.": {
        "recent_news": "Cybertruck deliveries ramping up",
        "stock_info": "Trading at $242, volatile quarter",
        "key_developments": "FSD v12 rollout, energy storage growth"
    }
}

def get_company_data(company_name: str):
    """
    Retrieves mock data for a given company name.
    Case-insensitive search.
    """
    normalized_name = company_name.strip()
    # Simple direct match first
    if normalized_name in mock_research:
        return mock_research[normalized_name]
    
    # Case insensitive match
    for k, v in mock_research.items():
        if k.lower() == normalized_name.lower():
            return v
    
    # Partial match
    for k, v in mock_research.items():
        if normalized_name.lower() in k.lower() or k.lower() in normalized_name.lower():
            return v
            
    return None
