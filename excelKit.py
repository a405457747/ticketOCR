import xlwings as xw


class excelKit:
    @staticmethod  
    def xlwingsObjects(filePath):
        # 应用->工作簿->工作表->范围
        # visible用于设置xlwings操作excel的过程是否显示，默认True表示显示
        # add_book表示xlwings操作excel的时候是否新增一个excel文件，默认是true
        app = xw.App(visible=False,add_book=False)
        #不显示Excel消息框
        app.display_alerts=False 
        #关闭屏幕更新,可加快宏的执行速度
        app.screen_updating=False 
        # 工作簿
        wb = app.books.open(filePath)

        return [app,wb];
    @staticmethod  
    #这个是添加多行
    def appendRowsXlwings(filePath, rowsData,sheetIdx=0):
        app,wb =excelKit.xlwingsObjects(filePath);

        # 工作表
        sht = wb.sheets[sheetIdx]

        for rowData in  rowsData:
            # 最后一行数目
            last_row=sht.range('A' + str(sht.cells.last_cell.row)).end('up').row
            # 追加然后保存
            rg=sht.range('A'+str(last_row+1));
            # 设置为文本化
            sht.range('A'+str(last_row+1)+":"+'H'+str(last_row+1)).api.NumberFormat = "@"

            rg.value =rowData;



        # 保存excel
        wb.save(filePath)
        # 关闭excel程序
        wb.close()
        app.quit()

    @staticmethod  
    #追加多行数据rowsData是二维数组
    def appendRows(filePath, rowsData,sheetIdx=0):
        '''
        rexcel = open_workbook(filePath) # 用wlrd提供的方法读取一个excel文件
        rows = rexcel.sheets()[0].nrows # 用wlrd提供的方法获得现在已有的行数
        excel = copy(rexcel) # 用xlutils提供的copy方法将xlrd的对象转化为xlwt的对象
        table = excel.get_sheet(0) # 用xlwt对象的方法获得要操作的sheet
        row = rows
        for i,dataItem in enumerate(listData):
            table.write(row, i, dataItem) # xlwt对象的写方法，参数分别是行、列、值
        excel.save(filePath) # xlwt对象的保存方法，这时便覆盖掉了原来的excel
        '''
        excelKit.appendRowsXlwings(filePath,rowsData,sheetIdx);

