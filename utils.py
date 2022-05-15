import re
import io
import glob
import os
import os.path
from shelve import Shelf
import shutil
from env import *


def command(command):
    os.system(command)


def varname(var):
    vnames = [name for name in globals() if globals()[name] is var]
    return vnames[0] if len(vnames) > 0 else None


def isMail(mailName):
    if os.path.isfile("app\\Mail\\{}Mail.php".format(mailName.replace("Mail", "").capitalize())):
        return True
    return False


def ask(question, possibleAnswers, options=[]):
    print("\n", question)
    for option in options:
        print(option)
    res = input("")

    if res == "exit":
        migrate() 
        print("\nthank u for using laraVite {}".format(VERSION))
        print("we hope to see u soon")
        exit()

    if res in possibleAnswers:
        return res
    print("please enter a valid answer")
    return ask(question, possibleAnswers, options=options)


def getLines(filePath):
    f = open(filePath, 'rt')
    lines = [line for line in f.readlines()]
    f.close()
    return lines


def write(filePath, content):
    f = open(filePath, 'w')
    f.write(content)
    f.close()


def replace(toReplace, replaceBy, filePath, count=0, line=0):
    if line == 0:
        f = io.open(filePath, "rt")
        content = f.read()
        f.close()

        f = io.open(filePath, "wt")
        newContent = re.sub(toReplace, replaceBy, content, count=count)
        f.write(newContent)
        f.close()

    else:
        lines = getLines(filePath)
        lines[line - 1] = re.sub(toReplace, replaceBy, lines[line - 1])
        write(filePath, "".join(lines))


def addLines(linesToAdd, filePath, position=0):
    lines = getLines(filePath)
    lines = lines[0:position] + linesToAdd + lines[position:]
    return lines


def findLines(regex, filePath, begin=1, end=0):
    lines = getLines(filePath)

    if end == 0:
        end = len(lines) + 1

    if lines != None:
        matching = []

        i = 0
        for line in lines:
            if begin - 1 < i < end - 1:
                if re.search(regex, line):
                    matching.append(i + 1)
            i += 1

        return matching
    return None


def deleteLines(begin, end, filePath):
    lines = getLines(filePath)
    lines = lines[:begin - 1] + lines[end - 1:]
    write(filePath, "".join(lines))
    
    return lines[begin - 1:end - 1]


def deleteLineWhere(regex, filePath):
    deletedLine = ""
    n = findLines(regex, filePath)
    if len(n) > 0:
        deletedLine = deleteLines(n[0], n[0] + 1, filePath)
    return deletedLine   


def fileIncludes(string, filePath, begin=1, end=0):
    f = io.open(filePath, 'rt')
    lines = [line for line in f.readlines()]
    hasVal = False
    f.close()

    if end == 0:
        end = len(lines) + 1        

    for line in lines[begin - 1:end - 1]:
        if string in line:
            hasVal = True

    return hasVal


def use(string, filePath):
    if not fileIncludes(string, filePath):
        lines = addLines(["use {};\n".format(string)], filePath, 4)
        write(filePath, "".join(lines))


def switchLines(n : int, m : int, filePath : str):
    lines = getLines(filePath)
    tmp = lines[n - 1]
    lines[n - 1] = lines[m - 1]
    lines[m - 1] = tmp
    write(filePath, "".join(lines))


def isModel(modelName):
    if os.path.isfile("app/Models/{}.php".format(modelName)):
        return True
    return False


def isEnv(name):
    if getEnv(name) != None:
        return True
    return False


def getEnv(name):
    lines = getLines('.env')
    for line in lines:
        a = re.findall(r"{}=([A-z0-9,.]+)".format(name), line)
        if len(a) > 0:
            return a[0]
    print("print no env named \"{}\" found /_/".format(name))
    return None


def setEnv(name, value):
    if fileIncludes(name, ".env"):
        oldValue = getEnv(name)
        replace("{}={}".format(name, oldValue), "{}={}".format(name, value), ".env")


def addEnv(name, value):
    if not fileIncludes(name, ".env"):
        lines = addLines(["{}={}\n".format(name, value)], ".env", len(getLines(".env")) + 1)
        write(".env", "".join(lines))


def migrate():
    if getEnv("LARAVITE_AUTO_MIGRATE") == "True":
        os.system("php artisan migrate:fresh --seed")


def getTabsAndSpaces(filePath, flag="toReplace"):
    tabs = 0
    spaces = 0
    lines = getLines(filePath) 
    for line in lines:
        if "{{-- {} --}}".format(flag) in line:
            for char in line:
                if ord(char) == 9:
                    tabs += 1
                elif ord(char) == 32:
                    spaces += 1
                else:
                    break
    return tabs, spaces


def component(name, args : dict, tabs=0, spaces=0, format="string"):
    lines = getLines(os.path.dirname(__file__) + "/components/{}.blade.php".format(name))

    # ##__isArg__??__then__##
    for i in range(len(lines)):
        matches = re.search("##(.*?)\?\?(.*?)##", lines[i])
        if matches != None:
            if matches.group(1).replace('__', '') in args:
                lines[i] = re.sub("##(.*?)\?\?(.*?)##", matches.group(2), lines[i])
            else:
                lines[i] = re.sub("##(.*?)\?\?(.*?)##", "", lines[i])

    for i in range(len(lines)):
        for key, value in args.items():
            lines[i] = lines[i].replace("__{}__".format(key), value)
        if i != 0:
            lines[i] = tabs * '\t' + spaces * ' ' + lines[i]

    if format == "list":
        return lines
    return "".join(lines)


def deleteComponent(component, filePath):
    lines = getLines(filePath)
    for i in range(len(lines)):
        print(i + 1)
        if component[0] in lines[i]:
            test = True
            for j in range(len(component)):
                if not component[j] in lines[i + j]:
                    test = False
                    print("False")
                    break
            if test == True:
                print("True")
                deleteLines(i + 1, i + len(component) + 1, filePath)
    

def addRoute(routeStr):
    if not fileIncludes(routeStr.split("\n")[0], "routes\\web.php"):
        lines = addLines(["\n{}".format(routeStr)], "routes\\web.php", len(getLines("routes\\web.php")))
        write("routes\\web.php", "".join(lines))
    else:
        print("route already exists /_/")


def addToNavbar(route, name):
    navbarPath = "resources/views/partials/backNavbar.blade.php"
    tabs, spaces = getTabsAndSpaces(navbarPath)
    if not fileIncludes("<a href=\"{{{{ route('{}') }}}}\">".format(route), navbarPath):
        replace("{{-- toReplace --}}", component("navbar-item", { 'route': '{}'.format(route), 'name': name.capitalize() }, tabs=tabs, spaces=spaces) + "\n\t\t\t{{-- toReplace --}}", navbarPath, 1)
    
        
def fontawesomeInit():
    if not fileIncludes("@fortawesome/fontawesome-free", "package.json"):
        os.system("npm install --save @fortawesome/fontawesome-free")

    if not fileIncludes("@fortawesome/fontawesome", "resources/sass/app.scss"):
        lines = addLines([
            "$fa-font-path: \"../webfonts\";\n",
            "@import \"~@fortawesome/fontawesome-free/scss/fontawesome\";\n",
            "@import \"~@fortawesome/fontawesome-free/scss/solid\";\n",
            "@import \"~@fortawesome/fontawesome-free/scss/brands\";\n",
            "@import \"~@fortawesome/fontawesome-free/scss/regular\";\n"
        ], "resources/sass/app.scss")
        write("resources/sass/app.scss", "".join(lines))

        os.system("npm run dev")

    else:
        print("fontawesome seems to be already initialized /_/")


def getIconLists():
    classIcons = None
    imgIcons = None

    if isEnv("LARAVITE_ICON_LISTS"):
        classIcons = getEnv("LARAVITE_ICON_LISTS").split(',')

    if isEnv("LARAVITE_IMG_ICON_LISTS"):
        imgIcons = getEnv("LARAVITE_IMG_ICON_LISTS").split(',')
        
    return classIcons, imgIcons


def askIconList(env):
    lists = getEnv(env).split(",")
    options = []
    possibleAnswers = []

    i = 1
    for l in lists:
        options.append("{}) {}".format(i, l))
        possibleAnswers.append(str(i))
        i += 1

    options.append("0) back")
    possibleAnswers.append("0")
        
    answ = ask("what list do you wanna use ?", possibleAnswers, options)

    if answ == "0":
        return None
    else:
        return lists[int(answ) - 1]


def getMethodHeight(method, filePath):
    begin = findLines("{}\(".format(method), filePath)[0] + 1
    end = None

    m = findLines("}", filePath)
    for i in m:
        if i > begin:
            end = i
            break
    
    return begin, end


def inMethod(method, string, filePath):
    begin, end = getMethodHeight(method, filePath)

    if fileIncludes(string, filePath, begin, end):
        return True
    return False


def addToMethod(method, content : list, filePath, doIfExisting=False):
    do = True

    if not doIfExisting:
        for line in content:
            if line != "\n":
                if inMethod(method, line, filePath):
                    do = False
                    break    
    
    begin, end = getMethodHeight(method, filePath)

    if do:        
        lines = addLines(content, filePath, begin)
        write(filePath, "".join(lines))
    else:
        print("content already in {} method /_/".format(method))



class Empty:
    pass



class Model:

    def __init__(self, model):

        # Names
        self.model = model.capitalize()
        self.modelLower = model.lower()
        self.table = self.modelLower + "s"
        self.inNavbar = True

        # Laravel Files
        files = [
            ("app/Models/{}.php".format(self.model), "php artisan make:model {}".format(self.model)), 
            ("app/Http/Controllers/{}Controller.php".format(self.model), "php artisan make:controller -r {model}Controller --model={model}".format(model = self.model)),
            ("database/migrations/*{}s_table*.php".format(self.modelLower), "php artisan make:migration create_{}_table".format(self.table)),
            ("database/seeders/*{}Seeder.php".format(self.modelLower), "php artisan make:seeder {}Seeder".format(self.model)),
            ("database/factories/*{}Factory.php".format(self.modelLower), "php artisan make:factory {}Factory".format(self.model))
        ]

        for file in files:
            if len(glob.glob(file[0])) <= 0:
                os.system(file[1])  

        self.modelPath = glob.glob("app\\Models\\{}.php".format(self.model))[0]
        self.controllerPath = glob.glob("app\\Http\\Controllers\\{}Controller.php".format(self.model))[0]
        self.migrationPath = glob.glob("database\\migrations\\*{}s*.php".format(self.modelLower))[0]
        self.seederPath = glob.glob("database\\seeders\\{}Seeder.php".format(self.model))[0]
        self.factoryPath = glob.glob("database\\factories\\{}Factory.php".format(self.model))[0]

        # Blades
        if not os.path.isdir("resources/views/back/{}".format(self.modelLower)):
            shutil.copytree(os.path.dirname(__file__) + '\\blades', "resources/views/back/{}".format(self.modelLower))

        self.indexPath = glob.glob("resources/views/back/{}/index.blade.php".format(self.modelLower))[0]
        self.createPath = glob.glob("resources/views/back/{}/create.blade.php".format(self.modelLower))[0]
        self.editPath = glob.glob("resources/views/back/{}/edit.blade.php".format(self.modelLower))[0]
        self.showPath = glob.glob("resources/views/back/{}/show.blade.php".format(self.modelLower))[0]

        replace("modelLower", self.modelLower, self.indexPath)
 

    def getColumns(self):
        columns = []
        n = findLines("\${}->save\(\);".format(self.modelLower), self.controllerPath)
        if len(n) > 0:
            lines = getLines(self.controllerPath)
            i = n[0] - 1
            
            while i > 0:
                if lines[i - 1] == "\n":
                    break

                col = re.search("\${}->([A-z0-9]+) = \$request".format(self.modelLower), lines[i - 1])
                if col is not None:
                    columns.append(col.groups()[0])
                i -= 1

        if len(columns) == 0:
            return None

        return columns[::-1]
            
        

    def addValidation(self, name):
        if not fileIncludes("validate([", self.controllerPath):
            linesN = findLines("{", self.controllerPath)
            lines = addLines(["\t\t$validated = $request->validate([\n", "\t\t]);\n", "\n"], self.controllerPath, linesN[6])
            write(self.controllerPath, "".join(lines))
            lines = addLines(["\t\t$validated = $request->validate([\n", "\t\t]);\n", "\n"], self.controllerPath, linesN[3])
            write(self.controllerPath, "".join(lines))

        if not fileIncludes("'{}' => 'required'".format(name), self.controllerPath):
            replace("validate\(\[", "validate([\n\t\t\t\'{}\' => \'required\',".format(name), self.controllerPath)

        else: 
            print("validation already added for this column /_/")



    def addColumnToSeeder(self, name, option):
        if not fileIncludes("use Illuminate\\Support\\Facades\\DB;", self.seederPath):
            replace("use Illuminate\\\\Database\\\\Seeder;", "use Illuminate\\\\Database\\\\Seeder;\nuse Illuminate\\\\Support\\\\Facades\\\\DB;", self.seederPath)

        if not fileIncludes("insert\(\[", self.seederPath):
            replace("\/\/", "DB::table('{}')->insert([\n\t\t\t'created_at' => now()\n\t\t]);".format(self.table), self.seederPath)

        value = "''"
        if option == 'integer' or option == 'foreignId':
            value = 1

        if not fileIncludes("'{}' => {}".format(name, value), self.seederPath):
            replace("insert\(\[", "insert([\n\t\t\t'{}' => {},".format(name, value), self.seederPath)


    def addLinesToStore(self, linesToAdd):
        storeLine = findLines("{", self.controllerPath)[3]
        lines = addLines(["\n\t\t", "\n\t\t".join(linesToAdd)], self.controllerPath, storeLine)


    def addColumnToStore(self, name, option):
        if not fileIncludes("::create([", self.controllerPath):
            print("to do : error handling addColumnToStore()")
            print("please report to the dev")
            print("thanks :)")

        col = "'{name}' => $request->{name},".format(name = name)
        if option == 'file':
            col = "'{name}' => 'storage/img/'.$request->{name}->hashName(),".format(name = name)
        elif option == 'sync':
            col = "${modelLower}->{name}()->sync($request->{name});".format(modelLower = self.modelLower, name = name)

        begin, end = getMethodHeight("store", self.controllerPath)
        if not fileIncludes(col, self.controllerPath, begin, end):
            
            if option == 'file':
                replace("\${modelLower} = {model}::create\(\[".format(modelLower = self.modelLower, model = self.model), "$request->{name}->storePublicly('img', 'public');\n\n\t\t${modelLower} = {model}::create([".format(modelLower = self.modelLower, model = self.model, name = name), self.controllerPath)
            elif option == 'sync':
                replace("return", "{}\n\n\t\treturn".format(col), self.controllerPath, 1, end - 1)
                col = "${modelLower}->{name}()->sync($request->{name});".format(modelLower = self.modelLower, name = name)
            else:
                replace("::create\(\[", "::create([\n\t\t\t{col}".format(col = col), self.controllerPath)
        
        else:
            print("column already exists in store methode /_/")


    def addColumnToUpdate(self, name, option):
        if option == 'file':
            if not fileIncludes("Illuminate\\Support\\Facades\\File;", self.controllerPath):
                replace("Illuminate\\\\Http\\\\Request;", "Illuminate\\\\Http\\\\Request;\nuse Illuminate\\\\Support\\\\Facades\\\\File;", self.controllerPath, 1)

        if not fileIncludes("${}->save();".format(self.modelLower), self.controllerPath):
            print("to do : error handling addColumnToUpdate()")
            print("please report to the dev")
            print("thanks :)")

        verif = "${modelLower}->{name} = ".format(modelLower = self.modelLower, name = name)
        if option == 'sync':
            verif = "${modelLower}->{name}()->sync($request->{name});".format(modelLower = self.modelLower, name = name)

        begin, end = getMethodHeight("update", self.controllerPath)
        if not fileIncludes(verif, self.controllerPath, begin, end):
            col = "${modelLower}->{name} = $request->{name};".format(modelLower = self.modelLower, name = name)
            if option == 'file':
                col = "if ($request->{name}) {{\n\t\t\tif(File::exists(public_path(${modelLower}->{name})))\n\t\t\t\tFile::delete(public_path(${modelLower}->{name}));\n\t\t\t${modelLower}->{name} = 'storage/img/'.$request->{name}->hashName();\n\t\t\t$request->{name}->storePublicly('img', 'public');\n\t\t}}".format(modelLower = self.modelLower, name = name)
            elif option == 'sync':
                col = "${modelLower}->{name}()->sync($request->{name});".format(modelLower = self.modelLower, name = name)

            replace("\${}->save\(\);".format(self.modelLower), "{col}\n\t\t${modelLower}->save();".format(modelLower = self.modelLower, col = col), self.controllerPath)

        else:
            print("column already exists in update methode /_/")


    def addColumnToDestroy(self, name, option):
        if option == "file":
            if not fileIncludes("Illuminate\\Support\\Facades\\File;", self.controllerPath):
                replace("Illuminate\\\\Http\\\\Request;", "Illuminate\\\\Http\\\\Request;\nuse Illuminate\\\\Support\\\\Facades\\\\File;", self.controllerPath, 1)

            addToMethod("destroy", [
                "\t\tif(File::exists(public_path(${}->{})))\n".format(self.modelLower, name),
                "\t\t\tFile::delete(public_path(${}->{}));\n".format(self.modelLower, name)
            ], self.controllerPath)


    def addColumnToMigration(self, name, option):
        if option == 'icon' or option == 'iconlist' or option == 'imgIcon':
            option = 'string'
            
        if not fileIncludes("$table->{}('{}')".format(option if option != "file" else "string", name), self.migrationPath):
            col = None
            if option == 'foreignId':
                col = "$table->foreignId('{}')->nullable()->constrained()->onDelete('cascade');".format(name)
            else:
                col = "$table->{}('{}');".format(option if option != "file" else "string", name)
            
            replace("id\(\);", "id();\n\t\t\t{}".format(col), self.migrationPath)
        else:
            print("column already exists in table {} /_/".format(self.table))


    def addColumnToFactory(self, name, option):
        if not fileIncludes("'{}' => '',".format(name), self.factoryPath):
            replace("\/\/", "'{}' => '',\n\t\t\t//".format(name), self.factoryPath)
        else:
            print("column already exists in factory {}Factory /_/".format(self.model))


    def addColumnToBlades(self, name, option, subOption):
        if not fileIncludes("<form", self.createPath):
            replace("{{-- toReplace --}}", '<form action="{{{{ route("{modelLower}.store") }}}}" method="POST" enctype="multipart/form-data">\n\t\t\t\t@csrf\n\t\t\t\t@method(\'POST\')\n\t\t\t\t{{{{-- toReplace --}}}}'.format(modelLower = self.modelLower), self.createPath)
        if not fileIncludes("<form", self.editPath):
            replace("{{-- toReplace --}}", '<form action="{{{{ route("{modelLower}.update", ${modelLower}) }}}}" method="POST" enctype="multipart/form-data">\n\t\t\t\t@csrf\n\t\t\t\t@method(\'PUT\')\n\t\t\t\t<input hidden type="text" name="_idvf" value="{{{{ encrypt(${modelLower}->id) }}}}">\n\t\t\t\t{{{{-- toReplace --}}}}'.format(modelLower = self.modelLower), self.editPath)

        inputType = "text"
        if option == "file":
            inputType = "file"

        otherModel = None
        if option == "foreignId":
            otherModel = Model(name.replace("_id", ""))

        # index
        if option == "file" or option == "imgIcon":
            index = "<td><img class=\"L-img\" src=\"{{{{ asset($item->{}) }}}}\"></img></td>".format(name)
        elif option == "foreignId" and subOption == "many":
            index = "<td class=\"L-tags\">\n\t\t\t\t\t\t\t@foreach ($item->{name}s as ${name})\n\t\t\t\t\t\t\t\t<span class=\"L-tag\">{{{{ ${name}->{firstCol} }}}}</span>\n\t\t\t\t\t\t\t@endforeach\n\t\t\t\t\t\t</td>".format(name = name.replace('_id', ''), firstCol = otherModel.getColumns()[0] if otherModel.getColumns() is not None else "id")
        elif option == "foreignId":
            index = "<td>{{{{ $item->{name} ? $item->{name}->{firstCol} : \"None\" }}}}</td>".format(name = name.replace('_id', ''), firstCol = otherModel.getColumns()[0] if otherModel.getColumns() is not None else "id")
        elif option == "icon" or option == "iconlist":
            index = "<td><i class=\"{{{{ $item->{} }}}}\"></i></td>".format(name)
        else:
            index = "<td>{{{{ $item->{} }}}}</td>".format(name)

        # edit / create
        createTabs, createSpaces = getTabsAndSpaces(self.createPath)
        editTabs, editSpaces = getTabsAndSpaces(self.editPath)

        if option == "foreignId" and subOption == "one_to_many":
            create = component("one-to-many-input", { 'name': name, 'name_upper': name.replace("_id", "").capitalize(), 'other_model_lower': name.replace("_id", ""), 'first_col': otherModel.getColumns()[0] if otherModel.getColumns() is not None else "id" }, createTabs, createSpaces)
            edit = component("one-to-many-input", { 'name': name, 'name_upper': name.replace("_id", "").capitalize(), 'other_model_lower': name.replace("_id", ""), 'first_col': otherModel.getColumns()[0] if otherModel.getColumns() is not None else "id", 'model_lower': self.modelLower }, editTabs, editSpaces)
        elif option == "foreignId" and subOption == "many":
            create = component("many-to-many-input", { 'name': name.replace("_id", ""), 'name_upper': name.replace("_id", "").capitalize(), 'first_col': otherModel.getColumns()[0] if otherModel.getColumns() is not None else "id" }, createTabs, createSpaces)
            edit = component("many-to-many-input", { 'name': name.replace("_id", ""), 'name_upper': name.replace("_id", "").capitalize(), 'first_col': otherModel.getColumns()[0] if otherModel.getColumns() is not None else "id", 'model_lower': self.modelLower }, editTabs, editSpaces)
        elif option == "icon":
            create = component("class-icon-input", { 'name': name, 'name_upper': name.capitalize(), 'icon_list': subOption.lower() }, createTabs, createSpaces)
            edit = component("class-icon-input", { 'name': name, 'name_upper': name.capitalize(), 'icon_list': subOption.lower(), 'model_lower': self.modelLower }, editTabs, editSpaces)
        elif option == "imgIcon":
            create = component("img-icon-input", { 'name': name, 'name_upper': name.capitalize(), 'icon_list': subOption.lower() }, createTabs, createSpaces)
            edit = component("img-icon-input", { 'name': name, 'name_upper': name.capitalize(), 'icon_list': subOption.lower(), 'model_lower': self.modelLower }, createTabs, createSpaces)
        elif option == "text":
            create = component("text-input", { 'name': name, 'name_upper': name.capitalize() }, createTabs, createSpaces)
            edit = component("text-input", { 'name': name, 'name_upper': name.capitalize(), 'model_lower': self.modelLower }, editTabs, editSpaces)
        else:
            create = component("base-input", { 'name': name, 'name_upper': name.capitalize(), 'type': inputType }, createTabs, createSpaces)
            edit = component("base-input", { 'name': name, 'name_upper': name.capitalize(), 'type': inputType, 'model_lower': self.modelLower }, editTabs, editSpaces)

        msg = []

        indexVerif = index
        if option == "foreignId" and subOption == "many":
            indexVerif = "@foreach ($item->{name}s as ${name})".format(name = name.replace("_id", ""))

        if not fileIncludes(indexVerif, self.indexPath):
            replace("<th>created_at<\/th>", "<th>{}</th>\n\t\t\t\t\t<th>created_at</th>".format(name.replace('_id', '').replace('_', ' ').capitalize()), self.indexPath)
            replace("{{-- toReplace --}}", "{}\n\t\t\t\t\t\t{{{{-- toReplace --}}}}".format(index), self.indexPath)
        else:
            msg.append("index")

        editCreateverif = '<label for="{name}" class="form-label">{nameUpper}</label>'.format(name = name, nameUpper = name.replace('_id', '').capitalize())
        if option == "foreignId" and subOption == "many":
            editCreateverif = 'name="{}s[]"'.format(name.replace("_id", ""))
            
        if not fileIncludes(editCreateverif, self.createPath):
            replace("{{-- toReplace --}}", "{}\n\t\t\t\t{{{{-- toReplace --}}}}".format(create), self.createPath)   
        else:
            msg.append("create")

        if not fileIncludes(editCreateverif, self.editPath):
            replace("{{-- toReplace --}}", "{}\n\t\t\t\t{{{{-- toReplace --}}}}".format(edit), self.editPath)
        else:
            msg.append("edit")

        if len(msg) > 0:
            print("column already exists in {} {} /_/".format(", ".join(msg), "blade" if len(msg) == 1 else "blades"))


    def routes(self):
        if not fileIncludes("use App\\Http\\Controllers\\{}Controller;".format(self.model), "routes/web.php"):
            replace("App\\\\Http\\\\Controllers\\\\WelcomeController;", "App\\\\Http\\\\Controllers\\\\WelcomeController;\nuse App\\\\Http\\\\Controllers\\\\{}Controller;".format(self.model), "routes/web.php")
        if not fileIncludes("Route::resource('/back/{}', {}Controller::class);".format(self.modelLower, self.model), "routes/web.php"):
            replace("Route::view\('\/back', 'layouts.back'\);", "Route::view('/back', 'layouts.back');\nRoute::resource('/back/{}', {}Controller::class);".format(self.modelLower, self.model), "routes/web.php")


    def initNavbar(self):
        addToNavbar("{}.index".format(self.modelLower), self.modelLower)


    def initDatabaseSeeder(self):
        if not fileIncludes("{}Seeder::class,".format(self.model), "database/seeders/DatabaseSeeder.php"):
            replace("\$this->call\(\[", "$this->call([\n\t\t\t{}Seeder::class,".format(self.model), "database/seeders/DatabaseSeeder.php")
        else:
            print("model already called in DatabaseSeeder /_/")


    def initController(self):
        if not fileIncludes("Illuminate\\Support\\Facades\\Schema;", self.controllerPath):
            replace("Illuminate\\\\Http\\\\Request;", "Illuminate\\\\Http\\\\Request;\nuse Illuminate\\\\Support\\\\Facades\\\\Schema;", self.controllerPath, 1)

        if not fileIncludes("use App\\Models\\{};".format(self.model), self.controllerPath):
            replace("Illuminate\\\\Http\\\\Request;", "Illuminate\\\\Http\\\\Request;\nuse App\\\\Models\\\\{};".format(self.model), self.controllerPath, 1)

        if len(findLines("\/\/", self.controllerPath)) == 7:
            replace("\/\/", '$all = {}::all();\n\t\t$columns = Schema::getColumnListing(\'{}\');\n\t\treturn view(\'back/{}.index\', compact(\'all\', \'columns\'));'.format(self.model, self.table, self.modelLower), self.controllerPath, 1)
            replace("\/\/", "return view('back/{}.create');".format(self.modelLower), self.controllerPath, 1)
            replace("\/\/", "${modelLower} = {model}::create([\n\t\t]);\n\n\t\treturn redirect()->route('{modelLower}.index')->with('success', '{model} successfully created');".format(model = self.model, modelLower = self.modelLower), self.controllerPath, 1)
            replace("\/\/", "return view('back/{modelLower}.show', compact('{modelLower}'));".format(modelLower = self.modelLower), self.controllerPath, 1)
            replace("\/\/", "return view('back/{modelLower}.edit', compact('{modelLower}'));".format(modelLower = self.modelLower), self.controllerPath, 1)
            replace("\/\/", "${modelLower}->save();\n\t\treturn redirect()->route('{modelLower}.index')->with('success', '{model} successfully updated');".format(model = self.model, modelLower = self.modelLower), self.controllerPath, 1)
            replace("\/\/", "${modelLower}->delete();\n\t\treturn back();".format(modelLower = self.modelLower), self.controllerPath, 1)

        else:
            print("controller already initialized /_/")

    
    def initModel(self):
        if not fileIncludes("protected $guarded = ['id'];", self.modelPath):
            replace("}", "\n\tprotected $guarded = ['id'];\n}", self.modelPath)

        else:
            print("model already initialized /_/")


    # out of date
    def addToWelcomeController(self):
        if not fileIncludes("'{}'".format(self.table), "app/Http/Controllers/WelcomeController.php"):
            replace("use Illuminate\\\\Http\\\\Request;", "use Illuminate\\\\Http\\\\Request;\nuse App\\\\Models\\\\{};".format(self.model), "app/Http/Controllers/WelcomeController.php")
            replace("index\(\) \{", "index() {{\n\t\t${} = {}::all();".format(self.table, self.model), "app/Http/Controllers/WelcomeController.php")
            replace("compact\(", "compact('{}',".format(self.table), "app/Http/Controllers/WelcomeController.php")


    def addToController(self, controllerName, options=['index', 'edit', 'create'], ass=None):
        controllerName = controllerName.replace("Controller", "").capitalize()
        controllerPath = "app/Http/Controllers/{}Controller.php".format(controllerName)

        if ass == None:
            ass = self.model

        if not fileIncludes("use App\\Models\\{};".format(self.model), controllerPath):
            replace("use Illuminate\\\\Http\\\\Request;", "use Illuminate\\\\Http\\\\Request;\nuse App\\\\Models\\\\{};".format(self.model), controllerPath)

        for option in options:
            beginMethodLine = findLines("{option}\(".format(option = option), controllerPath)[0] + 1

            n = findLines("}", controllerPath)
            for i in n:
                if i > beginMethodLine:
                    endMethodLine = i
                    break

            if not fileIncludes("${} = {}::all();".format(self.table, self.model), controllerPath, beginMethodLine, endMethodLine):
                replace("\{", "{{\n\t\t${} = {}::all();".format(self.table, self.model), controllerPath, 1, beginMethodLine)
                endMethodLine += 1

                if not fileIncludes("compact(", controllerPath, beginMethodLine, endMethodLine):
                    n = findLines("view", controllerPath, beginMethodLine, endMethodLine)
                    line = None
                    if len(n) > 0:
                        line = n[0]
                    if line != None:
                        replace("\'\)", "', compact())", controllerPath, 1, line)

                m = findLines("compact\(", controllerPath)
                for i in m:
                    if i > beginMethodLine:
                        if not fileIncludes("'{}'".format(self.table), controllerPath, i, i + 1):
                            replace("compact\(", "compact('{}', ".format(self.table), controllerPath, 1, i)
                        break

            else:
                print("model already inderted in {}@{} /_/".format(controllerName, option))


    # out of date
    def removeFromWelcomeController(self):
        deleteLineWhere("use App\\\\Models\\\\{};".format(self.model), "app/Http/Controllers/WelcomeController.php")
        deleteLineWhere("\${} = {}::all\(\);".format(self.table, self.model), "app/Http/Controllers/WelcomeController.php")
        replace("'{}',".format(self.table), "", "app/Http/Controllers/WelcomeController.php")


    def removeFromController(self, controllerPath):
        deleteLineWhere("use App\\\\Models\\\\{};".format(self.model), controllerPath)

        while fileIncludes("${} = {}::all();".format(self.table, self.model), controllerPath):
            deleteLineWhere("\${} = {}::all\(\);".format(self.table, self.model), controllerPath)

        replace("'{}', ".format(self.table), "", controllerPath)
        replace(", compact\(\)", "", controllerPath)


    def removeFromAllControllers(self):
        controllerPaths = glob.glob("app\\Http\\Controllers\\*")

        def filterFn(e):
            if e == 'app\\Http\\Controllers\\Auth':
                return False
            return True

        controllerPaths = filter(filterFn, controllerPaths)

        for path in controllerPaths:
            self.removeFromController(path)


    def init(self):
        self.initController()
        self.initDatabaseSeeder()
        self.routes()
        self.initNavbar()
        # self.addToWelcomeController()
        self.addToController("welcome", ['index'])
        self.initModel()
        
        print("\nmodel {} initialized +__+\n".format(self.model))


    def addColumn(self, name, option="string", subOption=""):
        env = "LARAVITE_ICON_LISTS"
        if option == "imgIcon":
            env = "LARAVITE_IMG_ICON_LISTS"

        if  option == "icon" or option == "imgIcon":
            subOption = askIconList(env)
            print("{} list chosen".format(subOption))

            if subOption != None:
                iconList = IconList(subOption)
                iconList.addToController(self.model)
            else:
                return None

        # migration / Seeder / Factory
        self.addColumnToMigration(name, option)
        self.addColumnToSeeder(name, option)
        self.addColumnToFactory(name, option)

        # Controller
        self.addColumnToStore(name, option)
        self.addColumnToUpdate(name, option)
        self.addColumnToDestroy(name, option)

        if option != "file":
            self.addValidation(name)

        # Blades
        self.addColumnToBlades(name, option, subOption)

        print("column {} added -__-".format(name))


    def addIdvfToMethods(self, filePath, methods=["edit", "update", "destroy", "show"]):
        for method in methods:
            line = findLines("public function {}\(".format(method), filePath)[0]

            if not fileIncludes('$request', filePath, line, line + 1):
                replace("\)", ", Request $request)", filePath, 1, line)
                
                # out of date
                # print("can't add idvf to {} method cause method needs access to Request /_/".format(method))
                # return 0

            addToMethod(method, ["\t\tif (decrypt($request->_idvf) != ${}->id)\n".format(self.modelLower),
                                 "\t\t\tabort(403);\n\n",
                            ], filePath)


    def addPolicies(self, condition=DEFAULT_POLICY_CONDITION, methods=["store", "update", "destroy"]):
        if not os.path.isfile("app/Policies/{}Policy.php".format(self.model)):
            os.system("php artisan make:policy {model}Policy --model={model}".format(model = self.model))
        else:
            print("policy already initialized in {}Controller /_/".format(self.model))

        pMethods = methods.copy()
        for i in range(len(pMethods)):
            if pMethods[i] == "store":
                pMethods[i] = "create"
            elif pMethods[i] == "destroy":
                pMethods[i] = "delete"

        use("Illuminate\\Support\\Facades\\Auth", "app/Policies/{}Policy.php".format(self.model))

        # implement policies functions
        for method in pMethods:
            if not fileIncludes("public function {}".format(method), "app/Policies/{}Policy.php".format(self.model)):
                replace("\n}", "\n\tpublic function() {}\n\t{{\n\t\t//\n\t}}".format(method), "app/Policies/{}Policy.php".format(self.model))
            # add return condition; to pMethods
            replace("\/\/", "return {};".format(condition), "app/Policies/{}Policy.php".format(self.model), 1, findLines("public function {}".format(method), "app/Policies/{}Policy.php".format(self.model))[0] + 2)

        # add policies to controller
        for i in range(len(methods)):
            arg = "{}::class".format(self.model)
            if methods[i] in ["update", "destroy"]:
                arg = "${}".format(self.modelLower)
            addToMethod(methods[i], ["\t\t$this->authorize('{}', {});\n".format(pMethods[i], arg), "\n"], self.controllerPath)
        

    def addGates(self, methods=["create", "edit"]):
        pMethods = methods.copy()
        for i in range(len(pMethods)):
            if pMethods[i] == "edit":
                pMethods[i] = "update"

        # AuthServiceProvider
        providerPath = "app\\Providers\\AuthServiceProvider.php"
        use("Illuminate\\Support\\Facades\\Gate", providerPath)
        use("App\\Policies\\{}Policy".format(self.model), providerPath)
            
        for i in range(len(methods)):
            addToMethod("boot", ["\t\tGate::define('{}-{}', [{}Policy::class, '{}']);\n".format(methods[i], self.modelLower, self.model, pMethods[i])], providerPath)

        # Controller
        use("Illuminate\Support\Facades\Gate", self.controllerPath)
        for i in range(len(methods)):   
            var = "" if methods[i] == "create" else ", ${}".format(self.modelLower)
            addToMethod(methods[i], ["\t\tGate::authorize('{}-{}'{});\n".format(methods[i], self.modelLower, var), "\n"], self.controllerPath) 


    def delete(self):
        files = [
            self.modelPath,
            self.controllerPath,
            self.migrationPath,
            self.seederPath,
            self.factoryPath,
            "app/Policies/{}Policy.php".format(self.model),
        ]

        for file in files:
            if os.path.isfile(file):
                os.remove(file)

        if os.path.isdir("resources/views/back/{}".format(self.modelLower)):
            shutil.rmtree("resources/views/back/{}".format(self.modelLower))

        if self.inNavbar:
            n = findLines("<a href=\"{{{{ route\('{}.index'\) }}}}\">".format(self.modelLower), "resources/views/partials/backNavbar.blade.php")
            if len(n) > 0:
                deleteLines(n[0] - 1, n[0] + 6, "resources/views/partials/backNavbar.blade.php")
        
        n = findLines("{}Seeder::class".format(self.model), "database/seeders/DatabaseSeeder.php")
        if len(n) > 0:
            deleteLines(n[0], n[0] + 1, "database/seeders/DatabaseSeeder.php")

        n = findLines("use App\\\\Http\\\\Controllers\\\\{}Controller;".format(self.model), "routes/web.php")
        if len(n) > 0:
            deleteLines(n[0], n[0] + 1, "routes/web.php")

        n = findLines("Route::resource\('\/back\/{}', {}Controller::class\);".format(self.modelLower, self.model), "routes/web.php")
        if len(n) > 0:
            deleteLines(n[0], n[0] + 1, "routes/web.php")

        # self.removeFromWelcomeController()
        self.removeFromAllControllers()

        print("\nmodel {} deleted :__:\n".format(self.model)) 



class IconList(Model):
    def __init__(self, model, type="class"):
        super().__init__(model)
        self.type = type

        self.env = "LARAVITE_ICON_LISTS"
        if self.type == "img":
            self.env = "LARAVITE_IMG_ICON_LISTS"
        

    def init(self):
        super().init()

        if not fileIncludes(self.env, ".env"):
            addEnv(self.env, self.model)
        else:
            if self.model not in getEnv(self.env):
                newValue = [self.model]+getEnv(self.env).split(",")
                setEnv(self.env, ",".join(newValue))

        if self.type == "img":
            self.addColumn("icon", "file")
        else:
            fontawesomeInit()
            self.addColumn("icon", "iconlist")


    def delete(self):
        super().delete()

        lists = getEnv(self.env).split(",")
        if self.model in lists:

            def filterFn(e):
                if e == self.model:
                    return False
                return True

            setEnv(self.env, ",".join(filter(filterFn, lists)))


class Pivot:
    def __init__(self, model, otherModel):
        self.model = model
        self.otherModel = otherModel
        self.table = "{}_{}".format(model, otherModel)

        if len(glob.glob("database\\migrations\\*create_{}_table.php".format(self.table))) == 0:
            os.system("php artisan make:migration create_{}_table".format(self.table))

        self.migrationPath = glob.glob("database\\migrations\\*create_{}_table.php".format(self.table))[0]


    def addColumn(self, name):           
        if not fileIncludes("$table->foreignId('{}')".format(name), self.migrationPath):
            col = "$table->foreignId('{}')->constrained()->onDelete('cascade');".format(name)
            replace("id\(\);", "id();\n\t\t\t{}".format(col), self.migrationPath)
        else:
            print("column already exists in table {} /_/".format(self.table))

    
    def init(self):
        self.addColumn("{}_id".format(self.model))
        self.addColumn("{}_id".format(self.otherModel))



class Job:
    def __init__(self, name):
        self.name = name
        self.path = "app/Jobs/{}Job.php".format(name.capitalize())


    def init(self):
        if not os.path.isfile(self.path):
            os.system("php artisan make:job {}Job".format(self.name))
        else:
            print("job {} already exists /_/".format(self.name))


    def handle(self, content : list):
        addToMethod("handle", content, self.path)
        # todo


    def delete(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

    # jobs
    # php artisan make:job JobName
    # php artisan queue:table to save jobs
    # php artisan queue:work to "watch" the queue
    

class Mail:
    def __init__(self, name):
        self.name = name
        self.path = "app\\Mail\\{}Mail.php".format(name)
        self.bladePath = "resources\\views\\emails\\{}.blade.php".format(name)


    def init(self):
        if not os.path.isfile(self.path):
            os.system("php artisan make:mail {}Mail".format(self.name.capitalize()))
        else:
            print("mail {}Mail already exists /_/".format(self.name.capitalize()))

        # Blades
        if not os.path.isdir("resources\\views\\emails"):
            os.mkdir("resources\\views\\emails")    

        if not os.path.isfile(self.bladePath):
            shutil.copyfile("{}\\mails\\example.blade.php".format(os.path.dirname(__file__)), self.bladePath)

        replace("view.name", "emails.{}".format(self.name), self.path)

        print("\nMail::to(\"mail@example.com\")->send(new {}Mail());\n".format(self.name.capitalize()))

        return "Mail::to(\"mail@example.com\")->send(new {}Mail());".format(self.name.capitalize())


    def addParam(self, name):
        if not fileIncludes("public ${};".format(name), self.path):
            replace("public function", "public ${};\n\tpublic function".format(name), self.path, 1)
            replace("__construct\(", "__construct(${}, ".format(name), self.path)
            addToMethod('__construct', ["\t\t$this->{} = ${};\n".format(name, name)], self.path)


    def delete(self):
        if os.path.isfile(self.path):
            os.remove(self.path)

        if os.path.isfile(self.bladePath):
            os.remove(self.bladePath)



class Listener:
    def __init__(self, name, event=None):
        self.name = name
        self.event = event
        self.path = "app\\Listeners\\{}Listener.php".format(name)


    def init(self):
        if not os.path.isfile(self.path):
            if self.event is not None:
                os.system("php artisan make:listener {}Listener --event={}Event".format(self.name.capitalize(), self.event.name.capitalize()))
            else:
                os.system("php artisan make:listener {}Listener".format(self.name.capitalize()))
        else:
            print("listener {}Listener already exists /_/".format(self.name.capitalize()))
            return 0



class Event:
    def __init__(self, name):
        self.name = name
        self.path = "app\\Events\\{}Event.php".format(name)
        self.listener = None

    
    def addListener(self, name=""):
        if name == "":
            name = self.name

        self.listener = Listener(name, self)
        self.listener.init()

        # eventServiceProvider
        use("App\\Listeners\\{}Listener".format(name.capitalize()), EVENT_PROVIDER_PATH)
        if not fileIncludes("{}Event::class => [".format(self.name.capitalize()), EVENT_PROVIDER_PATH):
            replace("protected \$listen = \[", "protected $listen = [\n\t\t{}Event::class => [\n\t\t],".format(self.name.capitalize()), EVENT_PROVIDER_PATH)  
        if not fileIncludes("{}Listener::class".format(name.capitalize()), EVENT_PROVIDER_PATH):
            replace("{}Event::class => \[".format(self.name.capitalize()), "{}Event::class => [\n\t\t\t{}Listener::class,".format(self.name.capitalize(), name.capitalize()), EVENT_PROVIDER_PATH)


    def init(self):
        if not os.path.isfile(self.path):
            os.system("php artisan make:event {}Event".format(self.name.capitalize()))
        else:
            print("event {} already exists /_/".format(self.name.capitalize()))

        self.addListener()

    
    def delete(self):
        # files
        if os.path.isfile(self.path):
            os.remove(self.path)
        if os.path.isfile(self.listener.path):
            os.remove(self.listener.path)

        # eventServiceProvider
        n = findLines("{}Event::class => \[".format(self.name.capitalize()), EVENT_PROVIDER_PATH)
        m = findLines("\],", EVENT_PROVIDER_PATH)
        if len(n) > 0 and len(m) > 0:
            for i in m:
                if i > n[0]:
                    deleteLines(n[0], i + 1, EVENT_PROVIDER_PATH)
                    break
        # coming soon bcs flemme



class Newsletter:
    def __init__(self, name="newsletter"):
        self.name = name
        self.controllerPath = "app\\Http\\Controllers\\{}Controller.php".format(self.name.capitalize())
        self.createBladePath = "resources\\views\\back\\{}\\create.blade.php".format(self.name)


    def init(self):
        if not os.path.isfile(self.controllerPath):
            os.system("php artisan make:controller {}Controller".format(self.name.capitalize()))
        else:
            print("controller {}Controller already exists /_/".format(self.name.capitalize()))

        # routes
        use("App\\Http\\Controllers\\{}Controller".format(self.name.capitalize()), "routes\\web.php")
        addRoute("Route::get('/back/{name}', [{nameUpper}Controller::class, 'create'])->name('{name}.create');".format(name = self.name, nameUpper = self.name.capitalize()))
        addRoute("Route::post('/back/{name}', [{nameUpper}Controller::class, 'send'])->name('{name}.send');".format(name = self.name, nameUpper = self.name.capitalize()))

        # navbar
        addToNavbar("{}.create".format(self.name), self.name)

        # blades
        if not os.path.isdir("resources\\views\\back\\{}".format(self.name)):
            os.mkdir("resources\\views\\back\\{}".format(self.name))
        
        if not os.path.isfile(self.createBladePath):    
            shutil.copyfile("{}\\newsletters\\example.blade.php".format(os.path.dirname(__file__)), self.createBladePath)
            replace("__name__", self.name, self.createBladePath)

        # controller
        use("App\\Models\\User", self.controllerPath)
        use("Illuminate\\Support\\Facades\\Mail", self.controllerPath)
        use("App\\Mail\\{}Mail".format(self.name.capitalize()), self.controllerPath)

        n = findLines("\{", self.controllerPath)[0]
        lines = []

        if not fileIncludes("public function send", self.controllerPath):
            lines = addLines([
                "\tpublic function send(Request $request)\n",
                "\t{\n",
                "\t\t$this->validate($request, [\n",
                "\t\t\t'subject' => 'required',\n",
                "\t\t\t'content' => 'required',\n",
                "\t\t]);\n",
                "\n",
                "\t\tforeach (User::where('{}ed', true)->get() as $user) {{\n".format(self.name),
                "\t\t\tMail::to($user->email)->send(new {}Mail($request->subject, $request->content));\n".format(self.name.capitalize()),
                "\t\t}\n",
                "\n",
                "\t\treturn redirect()->route('{}.create')->with('success', 'Mails successfully sent !');\n".format(self.name),
                "\t}\n",
                "\n",
            ], self.controllerPath, n)
        if len(lines) > 0:
            write(self.controllerPath, "".join(lines))
            lines = []

        if not fileIncludes("public function create", self.controllerPath):
            lines = addLines([
                "\tpublic function create()\n",
                "\t{\n",
                "\t\treturn view('back.{}.create');\n".format(self.name),
                "\t}\n",
                "\n"
            ], self.controllerPath, n)
        if len(lines) > 0:
            write(self.controllerPath, "".join(lines))

        # mail
        mail = Mail(self.name)
        mail.init()
        mail.addParam('content')
        mail.addParam('subject')
        if not fileIncludes("<p>{{ $content }}</p>", mail.bladePath):
            replace("<body>", "<body>\n\t<p>{{ $content }}</p>", mail.bladePath)
        replace("return \$this->view", "return $this->subject($this->subject)->view", mail.path)

        # userColumn
        userMigrationPath = glob.glob("database\\migrations\\*_create_users_table.php")[0]
        if not fileIncludes("$table->boolean('{}ed')".format(self.name), userMigrationPath):
            replace("\$table->id\(\);", "$table->id();\n\t\t\t$table->boolean('{}ed')->default(false);".format(self.name), userMigrationPath)


    def delete(self):
        # controller
        if os.path.isfile(self.controllerPath):
            os.remove(self.controllerPath)

        # routes
        deleteLineWhere("test.create", "routes\\web.php")
        deleteLineWhere("test.send", "routes\\web.php")

        # navbar
        navbarPath = "resources/views/partials/backNavbar.blade.php"
        n = findLines("<a href=\"{{{{ route\('{}.create'\) }}}}\">".format(self.name), navbarPath)
        if len(n) > 0:
            deleteLines(n[0] - 1, n[0] + 6, navbarPath)

        # blades
        if os.path.isdir("resources\\views\\back\\{}".format(self.name)):
            shutil.rmtree("resources\\views\\back\\{}".format(self.name))

        # mail
        mail = Mail(self.name)
        mail.delete()

        # userColumn
        print("\$table->boolean\('{}ed'\)".format(self.name))
        userMigrationPath = glob.glob("database\\migrations\\*_create_users_table.php")[0]
        deleteLineWhere("\$table->boolean\('{}ed'\)".format(self.name), userMigrationPath)


        

        

        


    
