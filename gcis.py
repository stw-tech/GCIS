import boto3
import json
import re
import time
import django
import os
client = boto3.client('cloudsearchdomain', 
  endpoint_url='https://search-gcis-muopck6cghhsxghgxg24adfhrm.ap-northeast-1.cloudsearch.amazonaws.com')

def generate_tree(search_keyword):
    # TODO try multi-thread to deal with time complexity problem
    # TODO use postgres db to fulfill this problem
    GCIS = {}
    search_keywords = []
    search_keywords.append(search_keyword)
    if(is_company(search_keyword)[0]=='false'):
        return "Please Key in a company name"
    elif(is_company(search_keyword)[0]=='Choose One'):
        return is_company(search_keyword)[1]
    else:
        GCIS['name'] = search_keyword
        GCIS['parent'] = "root"
        GCIS['children'] = []
        if(get_Person(search_keyword) != None):
            for i in get_Person(search_keyword):
                GCIS_level2 = {}
                GCIS_level2['name'] = i[0]
                GCIS_level2['attribute'] = i[1]
                GCIS_level2['children'] = []
                if(is_company(i[0])[0]=='false'):
                    level3 = get_Company(i[0])
                elif(is_company(i[0])[0]=='true'):
                    level3 = get_Person(i[0])
                for j in level3:
                    if(j not in search_keywords):
                        search_keywords.append(j)
                        if(j != None):
                            GCIS_level3 = {}
                            GCIS_level3['name'] = j
                            GCIS_level3['children'] = []
                            if(is_company(j)[0]=='false'):
                                level4 = get_Company(j)
                            elif(is_company(j)[0]=='true'):
                                level4 = get_Person(j)
                            for k in level4:
                                if(k not in search_keywords):
                                    search_keywords.append(k)
                                    if(k != None):
                                        GCIS_level4 = {}
                                        GCIS_level4['name'] = k[0]
                                        GCIS_level4['attribute'] = k[1]
                                        GCIS_level4['children'] = []
                                        if(is_company(k[0])[0]=='false'):
                                            level5 = get_Company(k[0])
                                        elif(is_company(k[0])[0]=='true'):
                                            level5 = get_Person(k[0])
                                        for l in level5:
                                            if(l not in search_keywords):
                                                search_keywords.append(l)
                                                if(l != None):
                                                    GCIS_level5 = {}
                                                    GCIS_level5['name'] = l
                                                    GCIS_level5['children'] = []
                                                    GCIS_level4['children'].append(GCIS_level5)
                                                else:
                                                    pass
                                        GCIS_level3['children'].append(GCIS_level4)
                                    else:
                                        pass
                            GCIS_level2['children'].append(GCIS_level3)
                        else:
                            pass
                GCIS['children'].append(GCIS_level2)
        return (GCIS)




def is_company(Name):
    '''
    Parameters
    ------------------------------
    Name: str
        What you want to check
    ------------------------------
    Return: list [status code, data (list)]
    '''
    data = []
    response = client.search(
        query='matchall',
        filterQuery ='(term field=company_name '+'\''+str(Name)+'\''+')',
        queryParser='structured'
    )
    if(response['hits']['found']==1):
        return ['true',[]]
    elif(response['hits']['found']>1):
        for i in response['hits']['hit']:
            data.append(i['fields']['company_name'][0])
        return ['Choose One',list(set(data))]
    else:
        return ['false',[]]
def get_Person(Company_name):
    '''
    Parameters
    -------------------------
    Company_name: str, Must
        A company name. (Must Check that the name is the only one)
    data: list
        A list of person and juristic_person && attribution
    '''
    data = []
    response = client.search(
        query='matchall',
        filterQuery ='(term field=company_name '+'\''+str(Company_name)+'\''+')',
        queryParser='structured'
    )
    if(response['hits']['found']>1):
        raise Exception('Company Name must be the only one!')
    elif(response['hits']['found']==1):
        for i in eval(response['hits']['hit'][0]['fields']['directors'][0]):
            if(i!='None'):
                data.append((i['Name'],"person"))
                if(i['Juristic_person'] != ''):
                    data.append((i['Juristic_person'],"Juristic_person"))
            else:
                return None
        return list(set(data))
    else:
        return None
def get_Company(Person_name):
    '''
    Parameters
    -------------------------------
    Person_name: str, Must
        Person name. (Included)
    data: list
        A list of company name
    '''
    data = []
    response = client.search(
        query='matchall',
        filterQuery ='(term field=directors '+'\''+str(Person_name)+'\''+')',
        queryParser='structured'
    )
    if(response['hits']['found']==0):
        return None
    for i in response['hits']['hit']:
        data.append(i['fields']['company_name'][0])
    return list(set(data))

# TODO deal with multiple company name
# TODO API for dump data into tree structure
# TODO API for check input character


if(__name__ == "__main__"):
    
    data = generate_tree("台灣積體電路製造股份有限公司")
    with open('data_v2.txt', 'w') as outfile:
        json.dump(data, outfile)