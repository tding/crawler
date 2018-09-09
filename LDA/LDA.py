'''
Created on Sep 20, 2016

@author: Tao Ding
'''
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from os import listdir
from os.path import isfile, join
import unicodecsv as csv
from gensim import corpora, models
from sklearn.cluster import KMeans
import numpy
from os import remove,path,makedirs,listdir
from os.path import isfile, join
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import operator

LDA_DIR = "D:/Dropbox/DrugAbuse/LDA/"
NUM_OF_TOPIC = [10]
NUM_OF_CLUSTER = [5]

tokenizer = RegexpTokenizer(r'\w+')
en_stop = get_stop_words('en')
p_stemmer = PorterStemmer()

def KMeanClustering():
    for numOfTopic in NUM_OF_TOPIC:
        lda_result_dir = LDA_DIR+str(numOfTopic)+"/"
        distribution_file = lda_result_dir + 'document-topic-distribution.csv';
        for num in NUM_OF_CLUSTER:
            kmean_result_dir = lda_result_dir+"KMEAN_"+str(num)+"/"
            if not path.exists(kmean_result_dir):
                makedirs(kmean_result_dir)
            
            reader=csv.reader(open(distribution_file,"rb"),encoding='utf-8')
            next(reader, None)
            x=list(reader)
            result=numpy.array(x).astype('float')
            kmeans = KMeans(n_clusters=num, init='k-means++', n_init=10, max_iter=300, tol=0.0001, precompute_distances='auto', verbose=0, random_state=None, copy_x=True, n_jobs=1)
            kmeans.fit(result[:,1:])
            
            
            centerWriter = csv.writer(open(kmean_result_dir+'centers.csv', 'wb'),encoding='utf-8')
            
            header = []
            header.append("id")
            for i in range(numOfTopic):
                header.append("Topic "+str(i))
            centerWriter.writerow(header)
            
            
            center_list = []
            for i,center in enumerate(kmeans.cluster_centers_):
                row = [int(i)]
                center_list.append([])
                for value in center:
                    row.append(value)
                centerWriter.writerow(row)
            
            labels = kmeans.labels_
            assignmentWriter = csv.writer(open(kmean_result_dir+'assignment.csv', 'wb'),encoding='utf-8')
            
            
            for i, index in enumerate(result[:,0]):
                dist = numpy.linalg.norm(result[i,1:]-kmeans.cluster_centers_[labels[i]])
                center_list[labels[i]].append((int(index),dist))
                assignmentWriter.writerow([int(index),labels[i],dist])
            
            sortedWriter = csv.writer(open(kmean_result_dir+'assignment_sorted.csv', 'wb'),encoding='utf-8')
            docsWriter = csv.writer(open(kmean_result_dir+'assignment_sorted_doc.csv', 'wb'),encoding='utf-8')
            
                
            for i,d in enumerate(center_list):
                sorted_d = sorted(d, key=lambda x: x[1])
                count = 0;
                for item in sorted_d:
                    sortedWriter.writerow([int(i),item[0],item[1]])
                    
                    if count < 20:
                        docsWriter.writerow([int(i),item[0],item[1]])
                    count = count + 1
                    
def retrieveWeight():
    top_docs = dict()
    for numOfTopic in NUM_OF_TOPIC:
        lda_result_dir = LDA_DIR+str(numOfTopic)+"/"
        for num in NUM_OF_CLUSTER:
            kmean_result_dir = lda_result_dir+"KMEAN_"+str(num)+"/"
            docs = kmean_result_dir+'retrievedDoc.csv'
            with open(docs, 'rb') as csvfile:
                spamreader = csv.reader(csvfile,encoding='utf-8')
                for row in spamreader:
                    top_docs[row[1]] = top_docs.get(row[1],0) + 1
                    
    
    
    annotation = csv.writer(open(LDA_DIR+'annotation_task.csv', 'wb'),encoding='utf-8')
    
    for numOfTopic in NUM_OF_TOPIC:
        lda_result_dir = LDA_DIR+str(numOfTopic)+"/"
        for num in NUM_OF_CLUSTER: 
            kmean_result_dir = lda_result_dir+"KMEAN_"+str(num)+"/"
            docs = kmean_result_dir+'retrievedDoc.csv'
            with open(docs, 'rb') as csvfile:
                spamreader = csv.reader(csvfile,encoding='utf-8')
                for row in spamreader:
                    weight = top_docs[row[1]]
                    if weight > 0:
                        annotation.writerow([row[1],row[2],weight])
                    top_docs[row[1]] = 0 
         
def retrieve():
    for numOfTopic in NUM_OF_TOPIC:
        lda_result_dir = LDA_DIR+str(numOfTopic)+"/"
        for num in NUM_OF_CLUSTER:
            kmean_result_dir = lda_result_dir+"KMEAN_"+str(num)+"/"
            sorted_file = kmean_result_dir+'assignment_sorted_doc.csv'
            doc_ids = []
            cluster_ids = []
            with open(sorted_file, 'rb') as csvfile:
                spamreader = csv.reader(csvfile,encoding='utf-8')
                for row in spamreader:
                    cluster_ids.append(row[0])
                    doc_ids.append(row[1])
            
            docs = [None] * len(doc_ids)
            links = [None] * len(doc_ids)
            
            files = [f for f in listdir(LDA_DIR) if isfile(join(LDA_DIR,f)) and "docs" in f and ".csv" in f]
        
            for file in files:
                with open(LDA_DIR+file, 'rb') as csvfile:
                    spamreader = csv.reader(csvfile,encoding='utf-8')
                    for row in spamreader:
                        if row[0] in doc_ids:
                            docs[doc_ids.index(row[0])] = row[3].lower()
                            links[doc_ids.index(row[0])] = row[1]
            
            docsWriter = csv.writer(open(kmean_result_dir+'retrievedDoc.csv', 'wb'),encoding='utf-8')
            for i,doc in enumerate(docs):
                docsWriter.writerow([cluster_ids[i],doc_ids[i],links[i], doc])
    
def LDA():
    files = [f for f in listdir(LDA_DIR) if isfile(join(LDA_DIR,f)) and "docs" in f and ".csv" in f]

    texts = []
    index = []
    
    for file in files:
        print file
        with open(LDA_DIR+file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            for row in spamreader:
                doc = row[3].lower()
                tokens = tokenizer.tokenize(doc)
                stopped_tokens = [i for i in tokens if not i in en_stop]
                stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
                if len(stemmed_tokens) > 2:
                    texts.append(stemmed_tokens)
                    index.append(row[0])
     
    dictionary = corpora.Dictionary(texts)
    dictionary.save()
    corpus = [dictionary.doc2bow(text) for text in texts]
    print len(corpus)
    
    
    for num in NUM_OF_TOPIC:
        lda_result_dir = LDA_DIR+str(num)+"/"
        if not path.exists(lda_result_dir):
            makedirs(lda_result_dir)
        
        if isfile(join(lda_result_dir,"model.model")):
            ldamodel = models.ldamodel.LdaModel.load(join(lda_result_dir,"model.model"),mmap='r')
        else:
            ldamodel = models.ldamodel.LdaModel(corpus, num_topics=num, id2word = dictionary, passes=20)
            ldamodel.save(lda_result_dir+"model.model")
        
        print "-------------",ldamodel.alpha
        textWriter = csv.writer(open(lda_result_dir+'topic.csv', 'wb'),encoding='utf-8')
        for i in range(num):
            textWriter.writerow(["Topic "+str(i)])
            for word in ldamodel.show_topic(i,20):
                textWriter.writerow([word[0],word[1]]);
            textWriter.writerow([]);
    
        disWriter = csv.writer(open(lda_result_dir+'document-topic-distribution.csv', 'wb'),encoding='utf-8')
        header = []
        header.append("id")
        for i in range(num):
            header.append("Topic "+str(i))
        disWriter.writerow(header)
    
        for i,bow in enumerate(corpus):
            distribution = [None] * (num+1)
            distribution[0]= index[i]
            for dis in ldamodel.get_document_topics(bow,minimum_probability=0):
                distribution[dis[0]+1] = dis[1]
            disWriter.writerow(distribution)   
            
def retrivalByHashTag(numOfTopic, numOfCluster, clusters, hashtags):
    lda_result_dir = LDA_DIR+str(numOfTopic)+"/"
    kmean_result_dir = lda_result_dir+"KMEAN_"+str(numOfCluster)+"/"
    plot_dir = kmean_result_dir+"plot/"
    
    if not path.exists(plot_dir):
        makedirs(plot_dir)
            
    assignment_file = kmean_result_dir+"assignment_sorted.csv"
    
    docs = []
    with open(assignment_file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            for row in spamreader:
                if int(row[0]) in clusters:
                    docs.append(row[1])
    
    dates = []
    files = [f for f in listdir(LDA_DIR) if isfile(join(LDA_DIR,f)) and "docs" in f and ".csv" in f]
    for file in files:
        with open(LDA_DIR+file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            for row in spamreader:
                if row[0] in docs:
                    doc = row[3].lower()
                    tokens = tokenizer.tokenize(doc)
                    if any(i in hashtags for i in tokens):
                        postDate = row[5].split("T")[0]
                        postMonth = postDate[:-3]
                        dates.append(postMonth)
    
    
    
    sortedDates = sorted(dates, key=lambda d: map(int, d.split('-')))
    dateDict = Counter(sortedDates);
    
    startYear = int(sortedDates[0].split("-")[0])
    startMonth = sortedDates[0].split("-")[1]
    endYear = int(sortedDates[-1].split("-")[0])
    endMonth = sortedDates[-1].split("-")[1]
     
    print startYear, endYear
    cfile = "";
    for c in clusters:
        cfile = cfile+str(c)+"_"
    cfile = cfile[:-1]
    
    totalPost = len(docs)
    relevantPost = len(dates)
    
    plotWriter = csv.writer(open(plot_dir+'plot_'+cfile+'.csv', 'wb'),encoding='utf-8')
    plotWriter.writerow([sortedDates[0],sortedDates[-1]])
    plotWriter.writerow([totalPost,relevantPost])
    
    months = ["01","02","03","04","05","06","07","08","09","10","11","12"];
    index = 1
    
    for y in range(startYear,endYear+1):
        if y == startYear:
            for m in months[months.index(startMonth):]:
                d = str(y)+"-"+m
                if d in dateDict:
                    plotWriter.writerow([index,dateDict[d]])
                else:
                    plotWriter.writerow([index,0])
                index = index + 1
            continue;
        if y == endYear:
            for m in months[:months.index(endMonth)+1]:
                d = str(y)+"-"+m
                if d in dateDict:
                    plotWriter.writerow([index,dateDict[d]])
                else:
                    plotWriter.writerow([index,0])
                index = index + 1
            continue;
        
        for m in months:
            d = str(y)+"-"+m
            if d in dateDict:
                plotWriter.writerow([index,dateDict[d]])
            else:
                plotWriter.writerow([index,0])
            index = index + 1
                    
def plot():
    for t in NUM_OF_TOPIC:
        for c in NUM_OF_CLUSTER:
            lda_result_dir = LDA_DIR+str(t)+"/"
            kmean_result_dir = lda_result_dir+"KMEAN_"+str(c)+"/"
            plot_dir = kmean_result_dir+"plot/"
            for i in range(c):
                with open(plot_dir+"plot_"+str(i)+".csv", 'rb') as csvfile:
                    spamreader = csv.reader(csvfile,encoding='utf-8')
                    line = 0
                    
                    start = ""
                    end = ""
                    total = ""
                    relevant = ""
                    X = []
                    Y = []
                    for row in spamreader:
                        if line == 0:
                            start = row[0];
                            end = row[1];
                            line = line + 1 
                            continue;
                        if line == 1:
                            total = row[0]
                            relevant = row[1];
                            precent = "{0:.2f}".format(float(relevant) / float(total))
                            line = line + 1 
                            continue;
                        X.append(int(row[0]))
                        Y.append(int(row[1]))
                    plt.clf()
                    plt.xlabel("Month ("+start+" to "+end+")",fontsize=18)
                    plt.ylabel("Posts",fontsize=18)
                    
                    plt.annotate('Total:'+total+" Retrieved:"+relevant+" Percentage:"+precent, xy=(0.05, 0.95), xycoords='axes fraction')
                    plt.plot(X, Y)
                    #plt.show()
                    plt.savefig(plot_dir+str(i)+".png")
                    #plt.scatter(X, Y, s=area, c=colors, alpha=0.5)

def getAnnoataion():
    annotation_file = LDA_DIR+"AnnotationTaskDrugRelated.csv"
    annotation = dict()
    with open(annotation_file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            spamreader.next()
            for row in spamreader:
                annotation[row[0]] = row[1]
    annotation_counter = Counter(annotation.values())
    
    for t in NUM_OF_TOPIC:
        plotWriter = csv.writer(open(LDA_DIR+str(t)+'clusterResult.csv', 'wb'),encoding='utf-8')
        for c in NUM_OF_CLUSTER:
            lda_result_dir = LDA_DIR+str(t)+"/"
            kmean_result_dir = lda_result_dir+"KMEAN_"+str(c)+"/"
            assignment_file = kmean_result_dir+"assignment_sorted.csv"
            clustering = dict()
            with open(assignment_file, 'rb') as csvfile:
                spamreader = csv.reader(csvfile,encoding='utf-8')
                for row in spamreader:
                    if row[0] in clustering:
                        clustering[row[0]]["count"] = clustering[row[0]]["count"] + 1 
                        if row[1] in annotation:
                            label = annotation[row[1]]
                            if label in clustering[row[0]]:
                                clustering[row[0]][label] = clustering[row[0]][label]+1
                            else:
                                clustering[row[0]][label] = 1
                    else:
                        clustering[row[0]] = dict()
                        clustering[row[0]]["count"] = 1
                        if row[1] in annotation:
                            label = annotation[row[1]]
                            clustering[row[0]][label] = 1
            plotWriter.writerow(["K="+str(c)])
            for i in range(0,c):
                h = str(i)
                print i,clustering[h]["count"]
                plotWriter.writerow(["cluster"+str(i),clustering[h]["count"]])
                plotWriter.writerow(["MedicalUse","DrugAbuse","Not Related","Not Sure"])
                docCount = []
                docPrecent = []
                for j in ['1', '2', '3','4']:
                    num = 0
                    numPrecent = 0.0
                    if j in clustering[h]:
                        num = clustering[h][j] #/ float(annotation_counter[j])
                        numPrecent = clustering[h][j] / float(annotation_counter[j])
                    docCount.append(num)
                    docPrecent.append(numPrecent)
                docCount.append(docCount[1] - docCount[2])
                docCount.append(docPrecent[1] - docPrecent[2])
                plotWriter.writerow(docCount)
            plotWriter.writerow([])

def subClustering(t,k,id,num):
    lda_result_dir = LDA_DIR+str(t)+"/"
    kmean_result_dir = lda_result_dir+"KMEAN_"+str(k)+"/"
    assignment_file = kmean_result_dir+"assignment_sorted.csv"
    
    kmean_result_subdir = kmean_result_dir+"sub/"
    docs_id = []
    
    with open(assignment_file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile,encoding='utf-8')
        for row in spamreader:
            if row[0] == id:
                docs_id.append(row[1])
                
    docs = []
    distribution_file = lda_result_dir + 'document-topic-distribution.csv';
    with open(distribution_file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile,encoding='utf-8')
        next(spamreader)
        i = 0
        for row in spamreader:
            if row[0] in docs_id:
                docs.append(row)
                i = i + 1
    
    print docs

    result=numpy.array(docs).astype('float')
    
    kmeans = KMeans(n_clusters=num, init='k-means++', n_init=10, max_iter=300, tol=0.0001, precompute_distances='auto', verbose=0, random_state=None, copy_x=True, n_jobs=1)
    kmeans.fit(result[:,1:])
    
    
    label = str(t)+'_'+str(k)+'_'+str(num);
    
    centerWriter = csv.writer(open(kmean_result_subdir+'subcenters_'+label+'.csv', 'wb'),encoding='utf-8')
    center_list = []
    for i,center in enumerate(kmeans.cluster_centers_):
        row = [int(i)]
        center_list.append([])
        for value in center:
            row.append(value)
        centerWriter.writerow(row)
    
    labels = kmeans.labels_
    assignmentWriter = csv.writer(open(kmean_result_subdir+'assignment'+label+'.csv', 'wb'),encoding='utf-8')
    
    
    for i, index in enumerate(result[:,0]):
        dist = numpy.linalg.norm(result[i,1:]-kmeans.cluster_centers_[labels[i]])
        center_list[labels[i]].append((int(index),dist))
        assignmentWriter.writerow([int(index),labels[i],dist])
    
    sortedWriter = csv.writer(open(kmean_result_subdir+'assignment_sorted'+label+'.csv', 'wb'),encoding='utf-8')
        
    for i,d in enumerate(center_list):
        sorted_d = sorted(d, key=lambda x: x[1])
        for item in sorted_d:
            sortedWriter.writerow([int(i),item[0],item[1]])

def evaluateAnnoation(t,k,id,num):
    annotation_file = LDA_DIR+"AnnotationTaskDrugRelated.csv"
    annotation = dict()
    with open(annotation_file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            spamreader.next()
            for row in spamreader:
                annotation[row[0]] = row[1]
    annotation_counter = Counter(annotation.values())
    
    lda_result_dir = LDA_DIR+str(t)+"/"
    kmean_result_dir = lda_result_dir+"KMEAN_"+str(k)+"/"
    kmean_result_subdir = kmean_result_dir+"sub/"
    label = str(t)+'_'+str(k)+'_'+str(num);
    
    assignment_file = kmean_result_subdir+"assignment_sorted"+label+".csv"
    clustering = dict()
    with open(assignment_file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile,encoding='utf-8')
        for row in spamreader:
            if row[0] in clustering:
                clustering[row[0]]["count"] = clustering[row[0]]["count"] + 1 
                if row[1] in annotation:
                    label = annotation[row[1]]
                    if label in clustering[row[0]]:
                        clustering[row[0]][label] = clustering[row[0]][label]+1
                    else:
                        clustering[row[0]][label] = 1
            else:
                clustering[row[0]] = dict()
                clustering[row[0]]["count"] = 1
                if row[1] in annotation:
                    label = annotation[row[1]]
                    clustering[row[0]][label] = 1
                    
    plotWriter = csv.writer(open(kmean_result_subdir+str(t)+'clusterResult'+label+'.csv', 'wb'),encoding='utf-8')
    plotWriter.writerow(["K="+str(k)])
    for i in range(0,k):
        h = str(i)
        print i,clustering[h]["count"]
        plotWriter.writerow(["cluster"+str(i),clustering[h]["count"]])
        plotWriter.writerow(["MedicalUse","DrugAbuse","Not Related","Not Sure"])
        docCount = []
        for j in ['1', '2', '3','4']:
            num = 0
            if j in clustering[h]:
                num = clustering[h][j] / float(annotation_counter[j])
            docCount.append(num)
        docCount.append(docCount[1] - docCount[2])
        plotWriter.writerow(docCount)
    plotWriter.writerow([])
    
    
if __name__ == '__main__':
    LDA()
    #KMeanClustering()
    #retrieve()
    #retrieveWeight()
    #getAnnoataion()
    #subClustering(10,5,'4',3)
    #evaluateAnnoation(10,5,'4',3)
    '''
    hashtags = ["fentanyl", "Apache", "ChinaGirl", "ChinaWhite", "DanceFever", "Friend", "Goodfella", "Jackpot", "Murder8", "TNT", "TangoCash", "GreatBear","ChinaTown", "HeMan", "KingIvory"]
    hashtags = [i.lower() for i in hashtags]
    
    for t in NUM_OF_TOPIC:
        for c in NUM_OF_CLUSTER:
            for i in range(c):
                retrivalByHashTag(t,c,[i],hashtags)
    '''
    #plot()