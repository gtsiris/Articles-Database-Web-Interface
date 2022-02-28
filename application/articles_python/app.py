# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import sys, os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0],
'lib'))
import pymysql as db
import settings


def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host,
        settings.mysql_user,
        settings.mysql_passwd,
        settings.mysql_schema)
    return con


def classify(topn):
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    query1 = "SELECT * FROM articles ar WHERE NOT EXISTS (SELECT * FROM article_has_class ahc WHERE ar.id=ahc.articles_id);"
    cur.execute(query1)
    articles_without_class = cur.fetchall()
    results_list = []
    for article in articles_without_class:
        summary = article[2]
        words = summary.split()
        relevant_classes = []
        for word in words:
            query2 = "SELECT cl.class, cl.subclass, cl.weight FROM classes cl WHERE cl.term=" + word + ";"
            cur.execute(query2)
            classes_with_this_term = cur.fertchall()
            for class1 in classes_with_this_term:
                relevant_classes.append([class1[0], class1[1], class1[2]])
        temp_results = []
        for i in range(len(relevant_classes)):
            for j in range(i):
                if i==0:
                    temp_results.append(relevant_classes[i])
                    break
                elif relevant_classes[i][0] == relevant_classes[j][0] and relevant_classes[i][1] == relevant_classes[j][1]:
                    for result in temp_results:
                        if result[0] == relevant_classes[i][0] and result[1] == relevant_classes[i][1]:
                            result[2] += relevant_classes[i][2]  #accumulate weightsum
                            break
                else:
                    temp_results.append(relevant_classes[i])
        for n in range(topn):
            most_relevant = temp_results[0]
            for result in temp_results:
                if result[2] > most_relevant[2]:
                    most_relevant = result
            results_list.append((article[1], most_relevant[0], most_relevant[1], most_relevant[2]))
            temp_results.remove(most_relevant)  #so we don't find the same one again and again
    return [("title","class","subclass", "weightsum"), results_list]


def updateweight(class1,subclass,weight):  #Warning: At webpage class1 and subclass must be given in string form: "..." or '...'
   # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    query = "SELECT cl.weight FROM classes cl WHERE cl.class=" + class1 + " AND cl.subclass=" + subclass + ";"
    cur.execute(query)
    weights = cur.fetchall()
    if weights == []:
        result = ["error"]
    else:
        upd = "UPDATE classes SET classes.weight=(classes.weight-" + weight + ")/2 WHERE classes.class =" + class1 + "AND classes.subclass =" + subclass + " AND classes.weight >" + weight + ";"
        cur.execute(upd)
        result = ["ok"]
    return [("result",), result]


def selectTopNClasses(fromdate, todate,n):
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    query = "SELECT cl.class, cl.subclass, COUNT(ar.id) FROM articles ar, article_has_class ahc, classes cl WHERE ar.id=ahc.articles_id AND ahc.class=cl.class AND ahc.subclass=cl.subclass AND ar.date>=" + fromdate + " AND ar.date<=" + todate + " GROUP BY cl.class, cl.subclass ORDER BY COUNT(ar.id) DESC LIMIT " + n + ";"
    cur.execute(query)
    top_classes = cur.fetchall()
    return [("class","subclass", "count"), top_classes]

def countArticles(class1,subclass):  #Warning: At webpage class1 and subclass must be given in string form: "..." or '...'
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    query = "SELECT COUNT(ar.id) FROM articles ar, article_has_class ahc, classes cl WHERE ar.id=ahc.articles_id AND ahc.class=cl.class AND ahc.subclass=cl.subclass AND cl.class=" + class1 + " AND cl.subclass=" + subclass + ";"
    cur.execute(query)
    count = cur.fetchall()
    return [("count",), count]


def JaccardSimilarity(set1, set2):
    if set1.isdisjoint(set2):
        similarity = 0
    else:
        similarity = len(set1.intersection(set2))/len(set1.union(set2))
    return similarity

def findSimilarArticles(articleId,n):
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    query1 = "SELECT ar.summary FROM articles ar WHERE ar.id=" + articleId + ";"
    cur.execute(query1)
    summary1, = cur.fetchone()
    set1 = set()
    words1 = summary1.split()
    set1.update(words1)
    query2 = "SELECT ar.id, ar.summary FROM articles ar WHERE ar.id!=" + articleId + ";"
    cur.execute(query2)
    temp_articles = cur.fetchall()
    articles = []
    for article in temp_articles:
        articles.append([article[0], article[1], 0])
    for article in articles:
        summary2 = article[1]
        set2 = set()
        words2 = summary2.split()
        set2.update(words2)
        article[2] = JaccardSimilarity(set1, set2)
    similar_articles = []
    for num in range(int(n)):
            most_similar = articles[0]
            for article in articles:
                if article[2] > most_similar[2]:
                    most_similar = article
            similar_articles.append((most_similar[0]))
            articles.remove(most_similar)  #so we don't find the same one again and again
    return [("articleid",), similar_articles]