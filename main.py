import email
import os
import re
from string import Template
import time
from tkinter import Tk, filedialog
from tkinter.messagebox import showinfo
import keyboard
import json
import tqdm
import pygetwindow as gw
import win32gui
def cleanTheSearch(context:str):
    if context.find("@SearchTags(") != -1:
        First = context.find("@SearchTags(") +12
        Second = context.find(")",First)
        context = context.replace(f"@SearchTags({context[First:Second]})","")
    return context

def getFileStr(path):
    if os.path.exists(path):
        with open(path,"r+",encoding="utf-8") as f:
            context = f.read()
            try:
                context = cleanTheSearch(context)
            except Exception as e:
                print(e)
            return re.findall(r"\"(.*?)\"",context)
    else:
        return []
    
def openFile(value:str):
    Path = filedialog.askdirectory(title=value)
    return Path

def sortTheMap(Map:dict):
    templist = []
    for black_str in Black_list:
        for key,value in Map.items():
            if key.startswith(black_str):
                templist.append(key)
    for i in templist:
        Map.pop(i)
    return Map

ignore_list = ["altmanager", "analytics", "event", "events", "hud", "mixin", "util","utils","keybinds","command","autolibrarian"]

Black_list = ["minecraft:","description.","multiplayer.","gui."]

class MainWindow:
    def __init__(self):
        self.index = 0
        self.SelectList:dict[int,list[str]] = {}
        self.UserChoice = 0
        self.ModName= ""
        self.hwnd = win32gui.GetForegroundWindow()
        self.showFileList()
        self.keyboard_start()


    
    def showFileList(self):
        self.SelectList.clear()
        self.UserChoice = 0

        os.system("cls")
        print("请选择Mod")
        time.sleep(1)

        if os.listdir("./Map") != []:
            for name,index in zip(os.listdir("./Map"),range(os.listdir("./Map").__len__())):
                self.createSelect(index,name,self.selectMod)
            self.showSelects()
        else:
            if not os.path.exists("./Map"):
                os.makedirs("./Map")
            with open("./Map/ModName.json","w",encoding="utf-8") as f:
                f.write("")
            print("你的映射文件夹是空的，已经为您创建新的Map.json，请重命名后使用")
            time.sleep(1)
            self.showFileList()

    def showSelects(self):
        os.system("cls")
        for key,value in self.SelectList.items(): 
            if self.UserChoice == key:
                print(f"{key}:{value[0]} <-------")
            elif self.UserChoice != key:
                print(f"{key} : {value[0]}")
    
    def putSelect(self):
        self.SelectList.clear()
        self.createSelect(0,"创建映射表",self.createMappingTable)
        self.createSelect(1,"切换Mod",self.showFileList)
        self.createSelect(2,"整理映射表",self.sortMapTabel)
        self.createSelect(3,"替换",self.replacecontext)
        self.createSelect(4,"翻译英文",self.translateNotChinese)
        self.createSelect(5,"更新映射表",self.updateMap)

        self.showSelects()

    def createMappingTable(self):
        keyboard.unhook_all()
        os.system("cls")
        print("注意！本次操作将会清空已有的列表，请注意是否为误触")
        # time.sleep(10)
        NewPath = openFile("选择未汉化的文件夹")
        OldPath = openFile("选择已经汉化的文件夹")
        NewList= []
        OldList = []
        TempDict = {}

        for (Odirpath,Oditnames,Ofilenames),(Ndirpath,Nditnames,Nfilenames) in zip(os.walk(OldPath),os.walk(NewPath)): #先遍历已经汉化过的目录
            skip = any(ignore_str in Odirpath for ignore_str in ignore_list)
            # print(skip)
            if not skip:
                for name in Ofilenames: #当前目录下面的文件
                    # print(f"{name}正在进行")
                    if name.endswith(".java"):
                        OldList = getFileStr(os.path.join(Odirpath,name)) #根据当前目录定位未汉化目录中的当前文件
                        NewList = getFileStr(os.path.join(Ndirpath,name)) #根据当前目录定位已经汉化目录中的当前文件
                    if NewList != [] and OldList != [] and NewList.__len__()==OldList.__len__(): 
                        for new,old in zip(NewList,OldList): #对比是否已经记录在内
                            if new not in TempDict.keys():
                                TempDict[new] = old #如果没有记录，则添加到字典中
                    elif NewList != [] and OldList != []:
                        print(f"{name}发生改动，不进行映射")
                        for new in NewList:
                            if new not in TempDict.keys():
                                TempDict[new] = new #如果没有记录，则添加到字典中，并将值设置为一样，表示未翻译
        with open(f"./Map/{self.ModName}.json","r+",encoding="utf-8") as f:
            f.seek(0)
            f.truncate()
            TempDict = sortTheMap(TempDict)
            json.dump(TempDict,f,ensure_ascii=False,indent=4)

        print("Succeed")
        print(f"请检查./Map/{self.ModName}.json")
        time.sleep(10)
        self.showSelects()
        self.keyboard_hook()

    def replacecontext(self):
        NewPath = openFile("选择未汉化的文件夹(将使用映射表)")
        for dirpath,ditnames,filenames in os.walk(NewPath):
            skip = any(ignore_str in dirpath for ignore_str in ignore_list)
            # print(skip)
            if not skip:
                for name in tqdm.tqdm(filenames):
                    if name.endswith(".java"):
                        with open(f"./Map/{self.ModName}.json","r",encoding="utf-8") as map:
                            Map:dict =  json.load(map)
                            with open(os.path.join(dirpath,name),"r+",encoding="utf-8") as f:
                                context = f.read()
                                for new,old in Map.items():
                                    context = context.replace(f'"{new}"',f'"{old}"')
                                f.seek(0)
                                f.truncate()
                                f.write(context)
        print("Succeed")
        time.sleep(10)
        self.showSelects()

    def translateNotChinese(self):
        self.UserChoice = 0
        def add():
            with open(f"./Map/{self.ModName}.json","r+",encoding="utf-8") as map:
                Map:dict = json.load(map)
                with open(f"./内容.json","r+",encoding="utf-8") as f:
                    templist = json.load(f)
                    for new,old in templist.items():
                        Map[new] = old
                    map.seek(0)
                    map.truncate()
                    json.dump(Map,map,ensure_ascii=False,indent=4)
            
            print("添加完成...")
            time.sleep(3)

            self.putSelect()

        with open(f"./Map/{self.ModName}.json","r",encoding="utf-8") as map:
            Map:dict = json.load(map)
            with open(f"./内容.json","w+",encoding="utf-8") as f:
                templist = {}
                for new,old in Map.items():
                    if not bool(re.compile(r"[\u4e00-\u9fff]").search(old)):
                        templist[new] = old
                json.dump(templist,f,ensure_ascii=False,indent=4)

        self.SelectList.clear()
        self.createSelect(0,"检查当前目录的 内容.json 完成就回车",add)
        self.showSelects()

    def selectMod(self):
        self.ModName = self.SelectList[self.UserChoice][0].replace(".json","")
        print(f"Now,mod's name is:{self.ModName}")
        time.sleep(3)
        self.putSelect()

    def sortMapTabel(self):
        with open(f"./Map/{self.ModName}.json","r+",encoding="utf-8") as f:
            Map = json.load(f)
            Map = sortTheMap(Map)
            f.seek(0)
            f.truncate()
            json.dump(Map,f,ensure_ascii=False,indent=4)
        print("Succeed")
        print(f"请检查./Map/{self.ModName}.json")
        time.sleep(3)
        self.showSelects()

    def updateMap(self):
        NewPath = openFile("选择未汉化")
        with open(f"./Map/{self.ModName}.json","r+",encoding="utf-8") as map:
            Map = json.load(map)
            templist= {}
            for dirpath,ditnames,filenames in os.walk(NewPath):
                skip = any(ignore_str in dirpath for ignore_str in ignore_list)
                if not skip:
                    for name in filenames:
                        if name.endswith(".java"):
                            Newlist = getFileStr(os.path.join(dirpath,name))
                            for new in Newlist:
                                templist[new] = new
            templist = sortTheMap(templist)
            for new,new2 in templist.items():
                if new not in Map.keys():
                    Map[new] = new
            
            map.seek(0)
            map.truncate()
            json.dump(Map,map,ensure_ascii=False,indent=4)
        os.system("cls")
        print("已完成")
        time.sleep(3)
        self.showSelects()
        

    def keyboard_hook(self):
        keyboard.on_press_key("up", self.on_up_arrow)
        keyboard.on_press_key("down", self.on_down_arrow)
        keyboard.on_press_key("enter", self.on_enter_arrow)

    def keyboard_start(self):
        self.keyboard_hook()
        keyboard.wait()

    def check(self):
        if self.UserChoice > self.SelectList.__len__()-1:
            self.UserChoice = 0
        if self.UserChoice < 0:
            self.UserChoice = self.SelectList.__len__()-1
    
    def createSelect(self,index,value,func):
        self.SelectList[index] = [value,func]

    def on_enter_arrow(self,event):
        if win32gui.GetForegroundWindow() == self.hwnd:
            self.SelectList[self.UserChoice][1]()

    def on_up_arrow(self,event):
        if win32gui.GetForegroundWindow() == self.hwnd:
            self.UserChoice -= 1
            self.check()
            self.showSelects()

    def on_down_arrow(self,event):
        if win32gui.GetForegroundWindow() == self.hwnd:
            self.UserChoice += 1
            self.check()
            self.showSelects()

if __name__ == "__main__":
    w = MainWindow()