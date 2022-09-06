
import os;
import shutil;   
import time;
import json;

from watchdog.observers import Observer


from pdf2image import convert_from_path

class controlFile:
    #原地重命名
    def situRenameFile(oldPath,newName):
        newPath =os.path.join(os.path.dirname(oldPath),newName+controlFile.pathFileSuffix(oldPath));
        if(os.path.exists(newPath)==False):
            os.rename(oldPath,newPath);


    def writeFile(file,content,mode="w"):
        with open(file,mode,encoding="utf-8") as f:
            f.write(content);

    def readFile(file,mode="r"):
        with open(file,mode,encoding='utf-8') as f :
            return f.read();

    def jsonWriteFile(filePath,dictObj):
        #dumps和dump区别，dump就是jsonWriteFile
        controlFile.writeFile(filePath,json.dumps(dictObj,indent=2));
    
    def jsonReadFile(filePath):
        strContent = controlFile.readFile(filePath);
        return json.loads(strContent);

    #对一个文件夹递归找到文件并放到绝对路径表中。
    def recursionGainFilePath(targetDir, filePathList, suffixWhiteList,dirBlackList=['node_modules','__pycache__']):
        files = os.listdir(targetDir)
        for file in files:
            file_rel = os.path.join(targetDir, file)
            if os.path.isdir(file_rel):
                if (file not in dirBlackList)and (file.startswith(".")==False):
                    controlFile.recursionGainFilePath(file_rel, filePathList, suffixWhiteList,dirBlackList)
            else:
                file_abs = os.path.abspath(file_rel)
                suffix = os.path.splitext(file_abs)[1]
                if suffix in suffixWhiteList:
                    filePathList.append(file_abs)

    #复制一个文件夹里面的文件到目录文件夹。
    def copyAllFileToTargetDirectory(fileDir,targetDir):
        files =os.listdir(fileDir);
        for file in files:
            #相对路径
            file_rel = os.path.join(fileDir, file)
            target_file_abs =os.path.join(targetDir,file);
            if os.path.isdir(file_rel) ==False:
                shutil.copy(file_rel,target_file_abs)

    #创建文件夹如果不存在。            
    def createDirectoryIfAbsence(filepath):
        if not os.path.exists(filepath):
            os.mkdir(filepath)
    #获取文件夹中的文件表,这个方法暂时没有后缀的过滤不够方便，不要去修改了，再开一个新方法即可
    def gainAllFilePath(fileDir,baseNameBlackList=[]):
        rel_path_list=[];
        files =os.listdir(fileDir);
        for file in files:
            file_rel = os.path.join(fileDir, file);
            baseName =os.path.basename(file_rel);
            if os.path.isdir(file_rel) ==False  and(baseName not  in baseNameBlackList):
                rel_path_list.append(file_rel);
        return rel_path_list;

    def gainAllFilePath2(fileDir,suffixBlackList=[]):
        rel_path_list=[];
        files =os.listdir(fileDir);
        for file in files:
            file_rel = os.path.join(fileDir, file);
            suffix =controlFile.pathFileSuffix(file_rel);
            if os.path.isdir(file_rel) ==False  and(suffix not  in suffixBlackList):
                rel_path_list.append(file_rel);
        return rel_path_list;

    #清空文件夹中的文件
    def clearAllFilePath(fileDir):
        files =controlFile.gainAllFilePath(fileDir);
        for file in files:
            os.unlink(file)
    
    #所有的文件路径复制到另一个文件夹中,这个方法局部了，所以更灵活要保留下来。
    def filePathsCopyToDir(imgFilePaths,targetDir):
        for imgFile in imgFilePaths:
            shutil.copyfile(imgFile,os.path.join(targetDir,os.path.basename(imgFile)));#这个方法第二个参数是文件夹
        pass;

    def pdfTwoImagePages(filePath):
        pages = convert_from_path(filePath, 500)
        return pages;

    def fileName(filePath):
        baseName =os.path.basename(filePath);
        suffiix =controlFile.pathFileSuffix(filePath);
        return baseName.replace(suffiix,"");

    def singlePdfTwoImage(filePath,suffix="JPEG"):
        pages = controlFile.pdfTwoImagePages(filePath);
        page =pages[0];
        fileDir =os.path.dirname(filePath);
        fileName ="PDF"+controlFile.fileName(filePath);
        writeFilePath =os.path.join(fileDir,fileName+".jpg");
        #print(fileDir,fileName,writeFilePath);
        page.save(writeFilePath, suffix);

    #获取文件后缀
    def pathFileSuffix(fileDir):
        return os.path.splitext(fileDir)[-1];
    #开始监听这个文件夹所有文件的变化，当变化时候vscode编辑会执行两次呢，奇怪用lessc也会引起变化而且是两次，哪怕内容都一致
    def startListenPathAllFile(path,event_handler,sleepNum=4.5,recursive=True):
        observer = Observer()
        observer.schedule(event_handler, path, recursive=recursive)
        observer.start()
        try:
            while True:
                time.sleep(sleepNum)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()