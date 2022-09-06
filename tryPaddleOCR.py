

import os
import re
import shutil


from controlFile import controlFile
from excelKit import excelKit
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"




from paddleocr import PaddleOCR
from PIL import Image

'''
ActOCR =PaddleOCR(

rec_model_dir="./commonInference/ch_ppocr_server_v2.0_rec_infer",
cls_model_dir="./commonInference/ch_ppocr_mobile_v2.0_cls_infer",
det_model_dir="./commonInference/ch_ppocr_server_v2.0_det_infer"


);
'''

ActOCR=PaddleOCR();

def dataIsMatch(itemStr,strFlag):    
    itemStr=itemStr.strip();
    matchObj = re.match( strFlag, itemStr,re.M)
    if matchObj:
        mRes =matchObj.group(1);

        return  mRes;
    else:
        return None;


def haveUseData(paddleOCR_results):
    res=[];
    for item1 in paddleOCR_results:
        dataItem =item1[1][0];
        res.append(dataItem);
    return res;

def useDataFind(useData,strFlag):
    res=[];
    for item in useData:
        matchRes=(dataIsMatch(item,strFlag));
        if(matchRes!=None):
            res.append(matchRes);
    return res;

def singleUseDataFind(useData,strFlag):
    res =useDataFind(useData,strFlag);
    if len(res)>=1:
        return res[0];
    else: 
        return "";

def idxUseDataFind(useData,strFlag,idxOffset=0):
    res =-1;
    for i, item in enumerate(useData):
        if((dataIsMatch(item,strFlag))!=None):
            res=i;
            break;
    if(res!=-1):
        return useData[(i+idxOffset)];
    else:
        return "";
def moneyIdxUseDataFind(useData,strFlag,idxOffset=0):
    res =-1;
    breakItem="";
    for i, item in enumerate(useData):
        if((dataIsMatch(item,strFlag))!=None):
            res=i;
            breakItem =item;
            break;
    if(res!=-1):
        if("¥" in breakItem) or("￥" in breakItem):
            return breakItem;
        else: 
            return useData[(i+idxOffset)];
    else:
        return "";


def readTicket(path):
    results =ActOCR.ocr(path);
    useData =haveUseData(results);
    return useData;

# 返回ticketDataArr数组
def dataTicket(path):
    useData =readTicket(path);
    #print("useDataItem is ");
    for item in useData:
        #print("【】"+item)
        pass
    
    #前面带一个中文 \u4e00-\u9fa5这个是汉字范围
    names =useDataFind(useData,r"称?[:： ]?([\u4e00-\u9fa5]{1}\w+[司院]$)");#0购买方，1是销售方
    buyName ="";
    sellName="";
    namesLength =len(names);
    #print("namesLength is ",namesLength,"arr:",names,"path is:",path);
    if(len(names)==2):#这里用了正则还是姚限制，因为没singleUseDataFind要找的严谨
        buyName= names[0];
        sellName=names[1];
    ticket_code =singleUseDataFind(useData,r"发?票?代?码?[:： ]?(\d{12}$)");
    ticket_number =singleUseDataFind(useData,r"发?票?号?码?[:： ]?(\d{8}$)");
    ticket_date =singleUseDataFind(useData,r"开?票?日?期?[:： ]?(\d{4}年\d{2}月\d{2}日$)");
    ticket_verify =singleUseDataFind(useData,r"校?[ ]?验?[ ]?码?[:： ]?(\d{5}[ ]?\d{5}[ ]?\d{5}[ ]?\d{5}$)");
    totalMoney=moneyIdxUseDataFind(useData,r"\W*(小写)\W*",1);

    return[buyName,sellName,ticket_code,ticket_number,ticket_date,ticket_verify,totalMoney]


def rotateImage(imgPath):
    im1= Image.open(imgPath);
    w,h =im1.size;

    baseName =os.path.basename(imgPath);

    isPdf="PDF" in baseName;
    if(isPdf):return;

    #竖的时候才旋转
    if(h>w):
        im2 =im1.rotate(90,expand=True);
        im2.save(imgPath);


def originalToPdfAndRotateImage(originalPath):
    filePaths= controlFile.gainAllFilePath(originalPath);
    pdfPaths =[filePath for filePath  in filePaths if controlFile.pathFileSuffix(filePath)==".pdf"];
    for pdfPath in pdfPaths:
        controlFile.singlePdfTwoImage(pdfPath);
    #print("pdfPaths is ",pdfPaths);

    #除了pdf就是图片了，这里转出来的不会变因为缓存的关系，filePaths还没有更新呢，嗯很好就要这样
    imgPaths =[filePath for filePath  in filePaths if controlFile.pathFileSuffix(filePath)!=".pdf"];
    for imgPath in imgPaths:
        rotateImage(imgPath);

#保存到excel表中
def saveTicketToExcel(listTicketDataArr,excelPath):
    excelKit.appendRows(excelPath,listTicketDataArr);

#发票重命名
def imgRename(imgPath,ticketDataArr):

    buyName =ticketDataArr[0];
    ticketNumber =ticketDataArr[3];
    sellName =ticketDataArr[1];
    newName =buyName+ticketNumber+sellName;  

    if("PDF" in os.path.basename(imgPath)):
        newName=newName+"PDF";

    if(newName!=""):
        controlFile.situRenameFile(imgPath,newName);
    else:
        print("发票有问题");

#把original中的图片(已经改名了)复制到changed文件夹
def ticketMove(imgFilePaths,targetDir):
    controlFile.filePathsCopyToDir(imgFilePaths,targetDir);

# 处理TicketDataArr
def handleTicketDataArr(originalPath,excelPath):
    #过滤掉pdf 
    imgFilePaths =controlFile.gainAllFilePath2(originalPath,[".pdf"]);
    #imgFilePaths=["./original/a3.jpg","./original/PDF7.jpg"]

    
    listTicketDataArr=[];
    for img in imgFilePaths:
        ticketDataArr=dataTicket(img);
        print("【想要的数据有】：",ticketDataArr)
        listTicketDataArr.append(ticketDataArr);
        imgRename(img,ticketDataArr);
        #print("dataItem is ",ticketDataArr[0]);
    

    #因为之前重命名了，所以强制更新一下这个路径表
    new_imgFilePaths =controlFile.gainAllFilePath2(originalPath,[".pdf"]);
    ticketMove(new_imgFilePaths,"./changed");

    #把original图片数据扔到excel表中
    saveTicketToExcel(listTicketDataArr,excelPath);

    #清空original?
    controlFile.clearAllFilePath(originalPath);

def testRe():
    print("res is :",dataIsMatch("111111111111",r"发?票?代?码?[:：]?(\d{12}$)"))

def printTestData():
    printHaveUseData("./original/7.jpg");
    printHaveUseData("./original/a3.jpg");
    printHaveUseData("./original/a4.jpg");
    printHaveUseData("./original/a5.jpg");

def printHaveUseData(path):
    results =ActOCR.ocr(path);
    for item1 in results:
        dataItem =item1[1][0];
        print(dataItem);

def process():
    originalPath="./original";
    excelPath ="./allData.xlsx";

    #original中把pdf弄成jpg,把发票给旋转一下卧槽
    originalToPdfAndRotateImage(originalPath);

    handleTicketDataArr(originalPath,excelPath);

def main():
    #testRe();
    process();


main();