import re
import shutil
import utils as u
import os
from init import init, isInitialized
from env import *


# TODO : mails
            # config/mail.php
            # php artisan make:mail MailName
            # return $this->from('mail@gmail.com')->view(emails.viewName); 
            # Mail::to('mail@gmail.com')->send(new MailName());
#        notifications
            # better with events/listeners
            # php artisan make:notification NotificationName
            # php artisan notification:table to save notifications


# morphRelashionships
# softDeletes
# [option] text DONE



def addColumn(model):
    print("to add column:")
    print("[column_name] [option]")
    print("leave empty when finished")

    while True:
        arr = input("").split(" ")

        if len(arr) == 1:
            if arr[0] == "":
                break
            column = arr[0]
            model.addColumn(column)
        elif len(arr) == 2:
            column, option = arr
            model.addColumn(column, option)
        elif len(arr) > 2:
            print("too many arguments")
            continue
        else:
            print("something bad occured :/")
            print("please try again !")


def createModel(modelName=""):
    if modelName == "":
        modelName = input("\nwhat name for the beautiful model u wanna create ?\n")
    model = None

    if u.isModel(modelName):
        print("\nmodel already exists /_/")
        answ = u.ask("Do u wanna modify it ? [y/n]", ["y", "n"])

        if answ == "y":
            modifyModel(modelName)
            return
        elif answ == "n":
            return

    model = u.Model(modelName)
    model.init()

    addColumn(model)


def addPoliciesAndGates(model):
    model.addPolicies()
    model.addGates()
    model.addIdvfToMethods(model.controllerPath)


def modifyModel(modelName=""):
    if modelName == "":
        modelName = input("\nWhich model do u wanna modify ?\n")
    
    model = None
    
    if not u.isModel(modelName):
        print("model doesn't exist yet :/")
        answ = u.ask("Do u wanna create the {} model ? [y/n]".format(modelName.capitalize()), ["y", "n"])

        if answ == "y":
            createModel(modelName)
            return
        else:
            return

    model = u.Model(modelName)
    model.init()

    action = u.ask("Possible actions:", ["1", "2", "3", "4", "0"], ["1) Add column", "2) Delete model", "3) Add relashionship", "4) Add Policies&Gates", "0) back"])

    if action == "0":
        return

    if action == "1":
        addColumn(model)

    elif action == "2":
        deleteModel(model)

    elif action == "3":
        addRelashionship(model.modelLower)

    elif action == "4":
        addPoliciesAndGates(model)


def deleteModel(model):
    answ = u.ask("U sure you want to delete the {} model ? [y/n]".format(model.model), ["y", "n"])

    if answ == "y":
        model.delete()
    else: 
        return


def hasOne(model, otherModel):
    if not u.fileIncludes("public function {}()".format(otherModel.modelLower), model.modelPath):
        n = u.findLines("}", model.modelPath)
        u.replace("}", "\n\tpublic function {}() \n\t{{\n\t\treturn $this->hasOne({}::class);\n\t}}\n}}".format(otherModel.modelLower, otherModel.model), model.modelPath, 0, n[len(n)-1])
    else:
        print("relashionship already exists in model {} /_/".format(model.model))


def hasMany(model, otherModel):
    if not u.fileIncludes("public function {}s()".format(otherModel.modelLower), model.modelPath):
        n = u.findLines("}", model.modelPath)
        u.replace("}", "\n\tpublic function {}s() \n\t{{\n\t\treturn $this->hasMany({}::class);\n\t}}\n}}".format(otherModel.modelLower, otherModel.model), model.modelPath, 0, n[len(n)-1])
    else:
        print("relashionship already exists in model {} /_/".format(model.model))


def belongsTo(model, otherModel):
    if not u.fileIncludes("public function {}()".format(model.modelLower), otherModel.modelPath):
        n = u.findLines("}", otherModel.modelPath)
        u.replace("}", "\n\tpublic function {}() \n\t{{\n\t\treturn $this->belongsTo({}::class);\n\t}}\n}}".format(model.modelLower, model.model), otherModel.modelPath, 0, n[len(n)-1])
    else:
        print("relashionship already exists in model {} /_/".format(otherModel.model))


def belongsToMany(model, otherModel, table):
    if not u.fileIncludes("public function {}s()".format(model.modelLower), otherModel.modelPath):
        n = u.findLines("}", otherModel.modelPath)  
        u.replace("}", "\n\tpublic function {}s() \n\t{{\n\t\treturn $this->belongsToMany({}::class, '{}');\n\t}}\n}}".format(model.modelLower, model.model, table), otherModel.modelPath, 0, n[len(n)-1])
    else:
        print("relashionship already exists in model {} /_/".format(otherModel.model))


def avoidIntegrityConstraintViolationInSeeder(model, otherModel):
    n = u.findLines("{}Seeder::class".format(model.model), "database/seeders/DatabaseSeeder.php")
    m = u.findLines("{}Seeder::class".format(otherModel.model), "database/seeders/DatabaseSeeder.php")

    if n[0] > m[0]:
        u.switchLines(n[0], m[0], "database/seeders/DatabaseSeeder.php")


def avoidIntegrityConstraintViolationInMigrations(model, otherModel):
    modelFileN = model.migrationPath.replace("database\\migrations\\", "").split("_")
    otherModelFileN = otherModel.migrationPath.replace("database\\migrations\\", "").split("_")

    while int(modelFileN[0]) >= int(otherModelFileN[0]):
        modelFileN[0] = int(modelFileN[0]) - 1

    modelFileN[0] = str(modelFileN[0])
    newPath = "database\\migrations\\" + "_".join(modelFileN)

    os.rename(model.migrationPath, newPath)
    model.migrationPath = newPath


def avoidIntegrityConstraintViolation(model, otherModel):
    avoidIntegrityConstraintViolationInSeeder(model, otherModel)
    avoidIntegrityConstraintViolationInMigrations(model, otherModel)


def oneToOne(model, otherModel):
    # addColumn
    otherModel.addColumn("{}_id".format(model.modelLower), "foreignId", "many")

    # model functions
    hasOne(model, otherModel)
    belongsTo(model, otherModel)

    # verify database seeder
    avoidIntegrityConstraintViolation(model, otherModel)

    print("relashionship \"{} has one {}\" added /_/".format(model.model, otherModel.model))
    

def oneToMany(model, otherModel):
    # addColumn
    otherModel.addColumn("{}_id".format(model.modelLower), "foreignId", "many")
    model.addToController(otherModel.modelLower)

    # model functions
    hasMany(model, otherModel)
    belongsTo(model, otherModel)

    # verify database seeder
    avoidIntegrityConstraintViolation(model, otherModel)

    print("relashionship \"{} has many {}\" added /_/".format(model.model, otherModel.model))


def manyToMany(model, otherModel):
    # init Pivot
    pivot = u.Pivot("rr", "tt")
    pivot.init()

    # controller
    # attach + detach
    model.addColumnToStore("{}s".format(otherModel.modelLower), "sync")
    model.addColumnToUpdate("{}s".format(otherModel.modelLower), "sync")
    otherModel.addColumnToStore("{}s".format(model.modelLower), "sync")
    otherModel.addColumnToUpdate("{}s".format(model.modelLower), "sync")

    # blades
    model.addColumnToBlades("{}_id".format(otherModel.modelLower), "foreignId", "many")
    otherModel.addColumnToBlades("{}_id".format(model.modelLower), "foreignId", "many")

    # other controller
    model.addToController(otherModel.modelLower)
    otherModel.addToController(model.modelLower)

    # model functions
    table = "{}_{}".format(model.modelLower, otherModel.modelLower)
    belongsToMany(model, otherModel, table)
    belongsToMany(otherModel, model, table)

    # verify integrations
    avoidIntegrityConstraintViolationInMigrations(model, pivot)
    avoidIntegrityConstraintViolationInMigrations(otherModel, pivot)

    print("relashionship \"many to many\" between {} and {} added /_/".format(model.model, otherModel.model))
    

def addRelashionship(modelName=""):
    if modelName == "":
        modelName = input("\nName of the first model :\n")

    otherModelName = input("\nName of the other model :\n")
    model = None
    otherModel = None

    if not u.isModel(modelName):
        print("model {} doesn't exists /_/".format(modelName.capitalize()))
        return
    if not u.isModel(otherModelName):
        print("model {} doesn't exists /_/'".format(otherModelName.capitalize()))
        return

    rel = u.ask("What are u yearning for ?", ["1", "2", "3", "0"], ["1) One to one", "2) One to many", "3) Many to many", "0) back"])

    if rel == "0":
        return
    else:
        model = u.Model(modelName)
        otherModel = u.Model(otherModelName)

    if rel == "1":
        answ = u.ask("Who is who ?", ["1", "2"], ["1) {} has one {}".format(model.model, otherModel.model), "2) {} has one {}".format(otherModel.model, model.model)])

        if answ == "1":
            oneToOne(model, otherModel)
        elif answ == "2":
            oneToOne(otherModel, model)

    elif rel == "2":
        answ = u.ask("Who is who ?", ["1", "2"], ["1) {} has many {}".format(model.model, otherModel.model), "2) {} has many {}".format(otherModel.model, model.model)])

        if answ == "1":
            oneToMany(model, otherModel)
        elif answ == "2":
            oneToMany(otherModel, model)

    elif rel == "3":
        manyToMany(model, otherModel)



def createIconList(iconListName=""):
    if iconListName == "":
        iconListName = input("\nhow do u wanna call it ?\n")
    iconList = None

    if u.isModel(iconListName):
        print("\niconList already exists /_/")
        return

    answ = u.ask("What kind of iconList do u wanna create ?", ["1", "2", "0"], ["1) based on class", "2) based on images", "0) back"])

    if answ == "0":
        return
    elif answ == "1":
        iconList = u.IconList(iconListName)
    elif answ == "2":
        iconList = u.IconList(iconListName, "img")
    else:
        print("\nsomething bad occured please report to dev :/\n")

    iconList.init()


def listIconLists():
    classIconList, imgIconList = u.getIconLists()
    if classIconList is not None:
        print("\nclass iconLists :")
        for iconList in classIconList:
            print("\t{}".format(iconList))
    else:
        print("no class iconLists found /_/")

    if imgIconList is not None:
        print("\nimg iconLists :")
        for iconList in imgIconList:
            print("\t{}".format(iconList))
    else:
        print("no img iconLists found /_/")

def deleteIconList(iconListName=""):
    if iconListName == "":
        iconListName = input("\nName of the iconList :\n")

    if not u.isModel(iconListName):
        print("iconList {} doesn't exists /_/".format(iconListName.capitalize()))
        return

    iconList = u.IconList(iconListName)
    iconList.delete()


def iconLists():
    answ = u.ask("What do u wanna do ?", ["1", "2", "3", "0"], ["1) create a new iconList", "2) list all iconLists", "3) delete iconList", "0) back"])

    if answ == "0":
        return
    elif answ == "1":
        createIconList()
    elif answ == "2":
        listIconLists()
    elif answ == "3":
        deleteIconList()
    else:
        print("\nsomething bad occured please report to dev :/\n")


def createMail(mailName):
    if mailName == "":
        name = input("\nName of the mail :\n")
    mail = u.Mail(name)
    mail.init()


def deleteMail(mailName=""):
    if mailName == "":
        mailName = input("\nName of the mail :\n")

    if not u.isMail(mailName):
        print("mail {} doesn't exists /_/".format(mailName.capitalize()))
        return

    mail = u.Mail(mailName)
    mail.delete()


def mails():
    answ = u.ask("What do u wanna do ?", ["1", "2", "0"], ["1) New mail", "2) Delete mail", "0) back"])

    if answ == "0":
        return
    elif answ == "1":
        createMail()
    elif answ == "2":
        deleteMail()
    else:
        print("\nsomething bad occured please report to dev :/\n")


def main():

    if not isInitialized():
        print("It seems your project isn't initialized yet /_/")
        answ = u.ask("Do u wanna initialize your project ? [y/n]", ["y", "n"])
        
        if answ == "y":
            init()
        else:
            print("U may encounter problems")
            answ = u.ask("You sure u wanna continue like this ? [y/n]", ["y", "n"])
            if answ == "n":
                init()

    while True:
        res = u.ask("what do u wanna do ?\n", ["1", "2", "3", "4", "5", "6", "0"], ["1) New Model", "2) Modify Model", "3) Add Relashionship", "4) IconLists", "5) Mails", "6) Coming Soon...", "0) exit"])

        if res == "1":
            createModel()

        elif res == "2":
            modifyModel()

        elif res == "3":
            addRelashionship()

        elif res == "4":
            iconLists()

        elif res == "5":
            mails()

        elif res == "6":
            print("\ncoming soon...\n")

        elif res == "0":
            u.migrate() 
            print("\nthank u for using laraVite {}".format(VERSION))
            print("we hope to see u soon")
            return 0

        u.migrate()
        # print("\nthank u for using laraVite {}".format(VERSION))
        # print("we hope to see u soon")







def test():
    u.isModel("tt")
    model = u.Model("tt")
    model.delete()

    u.isModel("rr")
    model = u.Model("rr")
    model.delete()

    otherModel = u.Model("tt")
    model = u.Model("rr")

    model.init()
    otherModel.init()

    # manyToMany(model, otherModel)
    model.addColumn("name", "text")
    # otherModel.addColumn("name")



main()    
# test()







def temp():
    portnames = ["PAN", "AMS", "CAS", "NYC", "HEL"]
    for portname in portnames:
        print(portname)
        


# temp()
