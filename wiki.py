import wikipedia

def wiki_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        print(summary)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "No page found."

