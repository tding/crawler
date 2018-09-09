'''
Created on Dec 1, 2016

@author: Tao Ding
'''

doc_a = "Tree are tree"
doc_b = "My mother spends a lot of time driving my brother around to baseball practice."
doc_c = "Some health experts suggest that driving may cause increased tension and blood pressure."


# compile sample documents into a list
doc_set = [doc_a, doc_b, doc_c]

from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')
raw = doc_a.lower()
tokens = tokenizer.tokenize(raw)

from stop_words import get_stop_words

# create English stop words list
en_stop = get_stop_words('en')

stopped_tokens = [i for i in tokens if not i in en_stop]

from nltk.stem.porter import PorterStemmer
# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()
texts = [p_stemmer.stem(i) for i in stopped_tokens]

from gensim import corpora, models

texts = [["test","tree"],["mother","spend"]]
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

ldamodel = models.ldamodel.LdaModel(corpus, num_topics=3, id2word = dictionary, passes=20,alpha=0.0001)
print "------",ldamodel.alpha

if __name__ == '__main__':
    pass