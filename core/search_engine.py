import requests
from bs4 import BeautifulSoup

def search_web(query):
    """يبحث في الويب ويعيد ملخصاً لأهم النتائج"""
    print(f"🌐 [SearchEngine] Searching for: {query}")
    # سنستخدم DuckDuckGo (نسخة HTML المبسطة) للبحث السريع
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        results = []
        for result in soup.find_all('a', class_='result__a')[:3]: # أول 3 نتائج
            results.append({
                'title': result.get_text(),
                'link': result.get('href')
            })
        
        if not results:
            return "لم يتم العثور على نتائج مباشرة في الويب."
            
        summary = "أهم النتائج التي وجدتها:\n"
        for r in results:
            summary += f"- {r['title']} ({r['link']})\n"
        return summary
        
    except Exception as e:
        return f"خطأ أثناء البحث: {str(e)}"

if __name__ == "__main__":
    # تجربة البحث عن حالة الطقس أو عملة
    print(search_web("سعر البيتكوين اليوم"))
