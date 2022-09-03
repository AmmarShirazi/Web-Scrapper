
#Project Phase 2
#Section:- A
#Group Members:-
#18i0603
#20i0402
#20i0405
#20i0409



from networkx.classes.function import degree
import requests
from bs4 import BeautifulSoup
import re
import spacy
import pandas as pd
import matplotlib.pyplot as plt
from spacy import displacy
from timeit import default_timer as timer
import networkx as nx

# assuming the url exists and doesn't return 404
def construct_bs_document(url):
    response = requests.get(url)
    html_text = response.text
    return BeautifulSoup(html_text, "html.parser")


def extract_all_strings(bs_document):
    strings = []
    all_tags = bs_document.find_all('h1')
    all_tags += bs_document.find_all('h2')
    all_tags += bs_document.find_all('h3')
    all_tags += bs_document.find_all('h4')
    all_tags += bs_document.find_all('h5')
    all_tags += bs_document.find_all('h6')
    all_tags += bs_document.find_all('p')
    for tag in all_tags:
        #strings.append(remove_nums_from_string(tag.text))
        strings.append(tag.text)
    return strings


def get_strings(url):
    return extract_all_strings(construct_bs_document(url))


def get_strings_from_multiple_urls(urls):
    words_list = []
    for url in urls:
        strings = get_strings(url)
        for string in strings:
            words_list.append(string)
    return words_list


def extract_spacy_doc(string):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(string)
    return doc


def extract_sentences(string):
    doc = extract_spacy_doc(string)
    return list(doc.sents)


fast = ['https://www.nu.edu.pk/', 'https://www.nu.edu.pk/Admissions/Scholarship', 'https://www.nu.edu.pk/Admissions/Scholarship', 'https://www.nu.edu.pk/University/History', 'https://www.nu.edu.pk/Admissions/HowToApply']
comsats = ['https://www.comsats.edu.pk/', 'http://ww3.comsats.edu.pk/scholarships/StudentsScholarships.aspx', 'http://ww3.comsats.edu.pk/rnd/Aboutus.aspx', 'http://ww3.comsats.edu.pk/ccrd/History.aspx', 'https://lahore.comsats.edu.pk/admissions/how_to_apply.aspx']
nust = ['https://nust.edu.pk/about-us', 'https://nust.edu.pk/admissions/scholarships/', 'https://rni.nust.edu.pk/research-and-innovation/', 'https://nust.edu.pk/about-us/history-of-nust/', 'https://nust.edu.pk/admissions/masters/instructions-for-online-application-form/']


def extract_pos(scrapped_data_list, nouns, adjectives, verbs):
    for x in scrapped_data_list:
        sentences = extract_sentences(x)
        for sentence in sentences:
            temp = sentence.text.strip()
            doc = extract_spacy_doc(temp)
            for token in doc:
                if token.pos_ == 'NOUN':
                    nouns.append(token.text)
                if token.pos_ == 'VERB':
                    verbs.append(token.text)
                if token.pos_ == 'ADJ':
                    adjectives.append(token.text)


start = timer()



fast_words = get_strings_from_multiple_urls(fast)
comsats_words = get_strings_from_multiple_urls(comsats)
nust_words = get_strings_from_multiple_urls(nust)

fast_nouns = []
fast_adjectives = []
fast_verbs = []

nust_nouns = []
nust_adjectives = []
nust_verbs = []

comsats_nouns = []
comsats_adjectives = []
comsats_verbs = []

extract_pos(fast_words, fast_nouns, fast_adjectives, fast_verbs)
extract_pos(nust_words, nust_nouns, nust_adjectives, nust_verbs)
extract_pos(comsats_words, comsats_nouns, comsats_adjectives, comsats_verbs)


def get_empty_graph(vertices):
    graph = dict()
    for vertice in vertices:
        graph[vertice] = []
    return graph


def construct_nouns_graph(nouns_list, scrapped_data_list):
    # nouns_list are the original vertices
    # we'll traverse each sentence and construct adjacent nouns graph from it
    graph = get_empty_graph(set(nouns_list))
    g = nx.Graph()
    nouns_in_a_sentence = []
    for x in scrapped_data_list:
        sentences = extract_sentences(x)
        for sentence in sentences:
            temp = sentence.text.strip()
            doc = extract_spacy_doc(temp)
            nouns_in_a_sentence = [token.text for token in doc if token.pos_ == 'NOUN']
            for noun in nouns_in_a_sentence:
                for x in nouns_in_a_sentence:
                    graph[noun].append(x)
    
    for key in graph.keys():
        for noun in graph[key]:
            g.add_edge(key, noun, weight=1)
    return g

def display_graph(g):
    nx.draw(g, with_labels=True)
    plt.draw()
    plt.show()


# CODE FOR VISUALIZING THE DATA (PART B)
print(len(fast_nouns), " ", len(fast_verbs), " ", len(fast_adjectives), "\n")
print(len(nust_nouns), " ", len(nust_verbs), " ", len(nust_adjectives), "\n")
print(len(comsats_nouns), " ", len(comsats_verbs), " ", len(comsats_adjectives), "\n")

fast_data = [len(fast_nouns), len(fast_verbs), len(fast_adjectives)]
nust_data = [len(nust_nouns), len(nust_verbs), len(nust_adjectives)]
comsats_data = [len(comsats_nouns), len(comsats_verbs), len(comsats_adjectives)]

index = ['Nouns', 'Verbs', 'Adjectives']
df = pd.DataFrame({'Fast': fast_data, 'Nust': nust_data, 'Comsats': comsats_data}, index = index)
ax = df.plot.bar(rot=0)
plt.show()

print('Select university you want to chose to create graph for: (1) FAST, (2) COMSATS, (3) NUST:')
option = input()
g = None
if option == '1':
    g = construct_nouns_graph(fast_nouns, fast_words)
elif option == '2':
    g = construct_nouns_graph(comsats_nouns, comsats_words)
elif option == '3':
    g = construct_nouns_graph(nust_nouns, nust_words)

total_components = nx.number_connected_components(g)
print(f"Total number of connected components: {total_components}")
degrees = dict(nx.degree(g))
nx.set_node_attributes(g,name='degree',values=degrees)
degree_df = pd.DataFrame(g.nodes(data='degree'), columns=['noun', 'degree'])
degree_df = degree_df.sort_values(by='degree', ascending=False)
degree_df[:10].plot(x='noun', y='degree', kind='barh').invert_yaxis()
plt.draw()
plt.show()

length = nx.all_pairs_shortest_path_length(g, 7)
length = list(length)
our_tuple = None
for pair in length:
    source, paths = pair
    if source == 'quality':
        our_tuple = pair
        break

if our_tuple == None:
    print("No noun 'quality' found in the website!")
    exit(1)

print('All the nouns with distance < 5 for the noun \'quality\' are: ')
_, linked_nouns = our_tuple
for noun in linked_nouns:
    if linked_nouns[noun] < 5:
        print(noun)

end = timer()
print(f"Execution took {end - start} seconds!")
