import requests

#! TODO:
#!      - Document and cleanup this code.

def get_best_definition(term):
    # Define the Urban Dictionary API endpoint
    url = "https://api.urbandictionary.com/v0/define"
    
    params = {'term': term}
    
    # Send the request to the API
    response = requests.get(url, params=params)
    
    # HTTP 200, success request
    if response.status_code == 200:
        data = response.json()
        
        if data['list']:
            # Sort the definitions by thumbs up votes
            sorted_definitions = sorted(data['list'], key=lambda x: x['thumbs_up'], reverse=True)
            best_definition = sorted_definitions[0]['definition']
            best_example = sorted_definitions[0]['example']
            return best_definition, best_example
        else:
            return "No definitions found for the term."
    else:
        return f"Error: {response.status_code}"

# # Example usage
# term = "Charizarding"
# result = get_best_definition_with_example(term)

# if isinstance(result, tuple):
#     best_definition, best_example = result
#     print(f"{best_definition}")
#     print(f"Example: {best_example}")
# else:
#     print(result)

