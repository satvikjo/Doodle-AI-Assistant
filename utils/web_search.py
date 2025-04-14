import wikipedia

def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Your query is too broad. Try something more specific like: {e.options[0]}"
    except wikipedia.exceptions.PageError:
        return "I couldn't find anything relevant on Wikipedia."
    except Exception:
        return "Something went wrong while searching Wikipedia."
