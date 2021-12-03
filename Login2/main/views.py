from django.shortcuts import render
from .models import UserInfo
from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseRedirect







        ##import 및 경로설정
import os
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from scipy import stats
# path = 'C:\Users\Gabriela Lee\Test\data\참빛설계'
#path = 'C:\\Users\\jessy\\Desktop\\kwcommons'
path = 'C:/Users/zofld/Desktop'
def prepare_card_data():
    ##비교용 카드데이터
    card_real_data = pd.read_csv(os.path.join(path, '카드데이터.csv'), encoding='utf-8')
    ##카드데이터에서 업종부분만 추출
    card_data_UPJONG = card_real_data.loc[3:16, :]
    ##업종별 이름순 정렬
    card_data_UPJONG = card_data_UPJONG.sort_values(by=card_data_UPJONG.columns[0], ascending=True)
    card_data_UPJONG = card_data_UPJONG.reset_index()
    card_data_UPJONG = card_data_UPJONG.drop(['index'],axis = 1)
    card_data = [card_real_data, card_data_UPJONG]
    return card_data

## 데이터에 있지 않은 업종도 최하위순위로 추가해주는 함수
def UPJONG_UNION(input_data):
    imsi = pd.DataFrame([['가전/가구'],
                     ['가정생활/서비스'],
                     ['교육/학원'],
                     ['미용'],
                     ['스포츠/문화/레저'],
                     ['여행/교통'],
                     ['요식/유흥'],
                     ['유통'],
                     ['음/식료품'],
                     ['의료'],
                     ['의류/잡화'],
                     ['자동차'],
                     ['전자상거래'],
                     ['주유']], columns = {'CLASS1'}
    )
    UNION_data = pd.merge(imsi, input_data, how = 'left', on = 'CLASS1' )
    ##UNION_data = UNION_data.drop(['Unnamed: 0', 'BLCK','성별','연령대별','카드이용건수계순위'],axis=1)
    UNION_data_new = pd.DataFrame()
    UNION_data_new['CLASS1'] = UNION_data['CLASS1']
    UNION_data_new['카드이용금액계순위'] = UNION_data['카드이용금액계순위']
    UNION_data2 = UNION_data_new.fillna(0)
    max_num = 0
    for i in UNION_data2['카드이용금액계순위'] :
        if i > max_num:
            max_num = i
    UNION_data_new = UNION_data_new.fillna(max_num + 1)
    return UNION_data_new


    ##지역데이터 index slicing
def search_index(input_data):
    index = 0
    compare = 0
    for i in input_data['CLASS1']:
        if((i =='가전/가구') & (compare<0)) : 
                compare = 0
                index += 1
        elif((i =='가정생활/서비스') & (compare<1)) : 
                compare = 1
                index += 1
        elif((i =='교육/학원') & (compare<2)) : 
                compare = 2
                index += 1
        elif((i =='미용') & (compare<3)) : 
                compare = 3
                index += 1
        elif((i =='스포츠/문화/레저') & (compare<4)) : 
                compare = 4
                index += 1
        elif((i =='여행/교통') & (compare<5)) : 
                compare = 5
                index += 1
        elif((i =='요식/유흥') & (compare<6)) : 
                compare = 6
                index += 1
        elif((i =='유통') & (compare<7)) :
                compare = 7
                index += 1
        elif((i =='음/식료품') & (compare<8)) : 
                compare = 8
                index += 1
        elif((i =='의료') & (compare<9)) : 
                compare = 9
                index += 1
        elif((i =='의류/잡화') & (compare<10)) :
                compare = 10
                index += 1
        elif((i =='자동차') & (compare<11)) : 
                compare = 11
                index += 1
        elif((i =='전자상거래') & (compare<12)) : 
                compare = 12
                index += 1
        elif((i=='주유') & (compare<13)): 
                compare = 13
                index += 1
    return index


def analysis_recommend(input_data, card_data) :
    ##개인소비데이터 업종별 순위 리스트 작성
    personal_rank_list = []
    for i in input_data['카드이용금액계순위']:
        personal_rank_list.append(i)
    card_similarity = [] ##유사도 저장용 리스트
    count = 1
    for i in card_data[1].iloc[:, 1:len(card_data[1])]:
        card_rank_data = card_data[1].iloc[:, [count]]
        card_ranking = card_rank_data.rank(method='min', ascending=False)
        card_rank = []
        for j in range(14) :
            card_rank.append(card_ranking.iloc[j,0])
        tau_similarity, p_value = stats.kendalltau(personal_rank_list, card_rank) ##유사도측정
        card_similarity.append(tau_similarity)
        count += 1
    ##가중치계산 준비
    input_data_Class=input_data[input_data['카드이용금액계순위']<6].sort_values(by=input_data.columns[1],ascending=True).iloc[:,0]
    ##가중치이용 총점계산
    card_score=['총점']
    for i in range(card_data[1].shape[1] - 1) :
        score=float(card_data[1].iloc[input_data_Class.index[0],i+1])*5/15 
        + float(card_data[1].iloc[input_data_Class.index[1],i+1])*4/15 
        + float(card_data[1].iloc[input_data_Class.index[2],i+1])*3/15 
        + float(card_data[1].iloc[input_data_Class.index[3],i+1])*2/15 
        + float(card_data[1].iloc[input_data_Class.index[4],i+1])*1/15
        card_score.append(score)
    data = card_data[0]
    data = data.append(pd.Series(card_score, index=data.columns), ignore_index=True)
    data_score = data.loc[17, :]
    ##상위3카드 점수계산, index추출
    first_card_index = 0
    first_card_score = 0
    second_card_index = 0
    second_card_score = 0
    third_card_index = 0
    third_card_score = 0
    change = 0
    for i in range(1,len(card_similarity)+1):
        if card_similarity[i-1] >= -1 : #특정유사도 이상
            if float(data_score[i]) > third_card_score:
                third_card_score = float(data_score[i])
                third_card_index = i
                if float(data_score[i]) > second_card_score:
                    change = second_card_score
                    second_card_score = third_card_score
                    third_card_score = change
                    change = second_card_index
                    second_card_index = third_card_index
                    third_card_index = change
                    if float(data_score[i]) > first_card_score:
                        change = first_card_score
                        first_card_score = second_card_score
                        second_card_score = change
                        change = first_card_index
                        first_card_index = second_card_index
                        second_card_index = change

    #상위3카드 결과출력
    card_name = data.loc[0, :]
    card1 = "1st카드 : "+ nocard(card_name[first_card_index])
    card2 = "2nd카드 : "+ nocard(card_name[second_card_index])
    card3 = "3rd카드 : "+ nocard(card_name[third_card_index])
    card = [card1 ,card2, card3]
    return card
    #print("1st카드 : %s, 카드점수 : %f" %(card_name[first_card_index], data_score[first_card_index]))
    #print("2st카드 : %s, 카드점수 : %f" %(card_name[second_card_index], data_score[second_card_index]))
    #print("3st카드 : %s, 카드점수 : %f" %(card_name[third_card_index], data_score[third_card_index]))
    #print()

def seoul_recommend(age, sex):
    seoul_data = pd.read_csv(os.path.join(path, '스울연령성별응용집계.csv'), encoding='utf-8')
    seoul_condition = (seoul_data['연령대별']==age)&(seoul_data['성별']==sex)
    seoul_data2 = seoul_data.loc[seoul_condition]
    seoul_index = search_index(seoul_data2)
    seoul_data2 = seoul_data2.reset_index()
    seoul_data = seoul_data2.loc[0:seoul_index]
    seoul_data = seoul_data.drop(['index', '성별', '연령대별', '카드이용건수계순위'], axis = 1)
    seoul_data = UPJONG_UNION(seoul_data)
    seoul_card = analysis_recommend(seoul_data, prepare_card_data())
    return seoul_card

def personal_recommend(input_data):
    ##개인소비데이터 불러오기 후, 업종별 합산 후, 순위작성
    personal_data = pd.read_csv(os.path.join(path, input_data), encoding='utf-8')
    df = personal_data.pivot_table(index=['CLASS1'], 
                                   values = ['카드이용건수계', '카드이용금액계'], aggfunc = 'sum')
    personal_Df = df.reset_index()
    ##personal_Df['카드이용건수계순위']=personal_Df['카드이용건수계'].rank(method='min',ascending=False)
    personal_Df['카드이용금액계순위']=personal_Df['카드이용금액계'].rank(method='min',ascending=False)
    personal_Df = personal_Df.drop(['카드이용건수계','카드이용금액계'], axis = 1)
    ##업종 개수 통일
    personal_Df = UPJONG_UNION(personal_Df)
    ##유사도 측정 및 카드추천
    print("<고객님의 소비패턴에 맞추어 혜택을 가장 많이 줄 수 있는 카드>")
    card = analysis_recommend(personal_Df, prepare_card_data())
    return card

def local_recommend(gu_address, dong_address, age, sex, year_month) :
    ##구별, 동별데이터 각각 불러오기
    gu_local_data = pd.read_csv(os.path.join(path, '구대학가연령성별응용집계_'+year_month+'.csv'),
                               encoding = 'utf-8')
    dong_local_data = pd.read_csv(os.path.join(path, '동대학가연령성별응용집계_'+year_month+'.csv'),
                               encoding = 'utf-8')
    
    ##입력 지역으로 필터링 후, 업종 개수 통일
    gu_condition=(gu_local_data['연령대별']==age)&(gu_local_data['성별']==sex)&(gu_local_data['SIGNGU_CD']==gu_address)
    dong_condition=(dong_local_data['연령대별']==age)&(dong_local_data['성별']==sex)&(dong_local_data['BLCK']==dong_address)
    
    gu_local_data2 = gu_local_data.loc[gu_condition]
    gu_index = search_index(gu_local_data2)
    gu_local_data2 = gu_local_data2.reset_index()
    gu_local_data = gu_local_data2.loc[0:gu_index]
    gu_local_data = gu_local_data.drop(['index','Unnamed: 0', 'SIGNGU_CD','성별','연령대별','카드이용건수계순위'], axis = 1)
    gu_local_data = UPJONG_UNION(gu_local_data)
    
    dong_local_data2 = dong_local_data.loc[dong_condition]
    dong_index = search_index(dong_local_data2)
    dong_local_data2 = dong_local_data2.reset_index()
    dong_local_data = dong_local_data2.loc[0:dong_index]
    dong_local_data = dong_local_data.drop(['index','Unnamed: 0', 'BLCK','성별','연령대별','카드이용건수계순위'], axis = 1)
    dong_local_data = UPJONG_UNION(dong_local_data)
    
    if sex == 'M':
        sex2 = '남성'
    else :
        sex2 = '여성'
    #같은 구에 사는, 같은 동에 사는, 같은 연련령대, 성별을 가지고있는 사람들의 소비패턴에 추천되는 카드
    ##print("<"+gu_address+"에 사는 "+age+" "+sex2+"의 소비패턴에 추천되는 카드>")
    ##print("<%s에 사는 %s %s의 소비패턴에 추천되는 카드>" %(gu_address, age, sex2))
    ##text = analysis_recommend(gu_local_data, prepare_card_data())
    ##return text
    ##print("<"+dong_address+"에 사는 "+age+" "+sex2+"의 소비패턴에 추천되는 카드>")
    #print("<%s에 사는 %s %s의 소비패턴에 추천되는 카드>" %(dong_address, age, sex2))
    gu_card = analysis_recommend(gu_local_data, prepare_card_data())
    dong_card = analysis_recommend(dong_local_data, prepare_card_data())
    local_card = [gu_card, dong_card]
    return local_card

def setResult():
    gu = request.POST.get("gu")
    dong = request.POST.get("dong")
    age = request.POST.get("age")
    sex = request.POST.get("sex")
    file = request.POST.get("file")

def nocard(cardresult):
    if cardresult == "카드명" :
        return "추천된 카드가 부족합니다."
    else :
        return cardresult


class Login(View):
    def get(self, request):
        return render(request, 'main/login.html')
    def post(self, request):
        gu = request.POST.get("gu")
        dong = request.POST.get("dong")
        age = request.POST.get("age")
        sex = request.POST.get("sex")
        file = request.POST.get("file")

        perso_card1 = True
        perso_card2 = True
        perso_card3 = True
        gu_text = True
        gu_card1 = True
        gu_card2 = True
        gu_card3 = True
        dong_text = True
        dong_card1 = True
        dong_card2 = True
        dong_card3 = True
        seoul_card1 = True
        seoul_card2 = True
        seoul_card3 = True

        if sex == 'M':
            sex2 = '남성'
        else :
            sex2 = '여성'
        personal_result = personal_recommend(file)
        perso_card1 = personal_result[0]
        perso_card2 = personal_result[1]
        perso_card3 = personal_result[2]

        local_card = local_recommend(gu, dong, age, sex, "201903")

        gu_text = gu + ' ' + age + ' ' + sex2 + '거주자 추천 카드'
        gu_card1 = local_card[0][0]
        gu_card2 = local_card[0][1]
        gu_card3 = local_card[0][2]

        dong_text = dong + ' ' + age + ' ' + sex2 + '거주자 추천 카드'
        dong_card1 = local_card[1][0]
        dong_card2 = local_card[1][1]
        dong_card3 = local_card[1][2]

        seoul_result = seoul_recommend(age, sex)
        seoul_card1 = seoul_result[0]
        seoul_card2 = seoul_result[1]
        seoul_card3 = seoul_result[2]

        context = {
            'Result':'Result',
            'perso_card1':perso_card1,
            'perso_card2':perso_card2,
            'perso_card3':perso_card3,
            'gu_text':"<<" + gu_text + ">>",
            'gu_card1':gu_card1,
            'gu_card2':gu_card2,
            'gu_card3':gu_card3,
            'dong_text':"<<" + dong_text + ">>",
            'dong_card1':dong_card1,
            'dong_card2':dong_card2,
            'dong_card3':dong_card3,
            'personaltext':"<<개인소비내역 기반 추천 카드>>",

            'seoul_text':"<<서울시민 추천 카드>>",
            'seoul_card1':seoul_card1,
            'seoul_card2':seoul_card2,
            'seoul_card3':seoul_card3,

        }
        return render(request, 'main/login.html', context)

"""
# Create your views here.
class Login(View):
    def get(self, request):
        return render(request, 'main/login.html')
    def post(self, request):
        id=request.POST.get("userid")
        pw=request.POST.get("userpw")
        msg=False
        infos=UserInfo.objects.all()
        for info in infos:
            if info.userid==id and info.userpw==pw:
                name=info.username
                msg = True
        msg = name+'님, 로그인에 성공'

        context = {
            'msg':msg,
        }
        return render(request, 'main/result.html', context)
"""