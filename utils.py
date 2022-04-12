import re
import io
import glob
import os
import os.path
import shutil


def command(command):
    os.system(command)


def ask(question, possibleAnswers, options=[]):
    print("\n", question)
    for option in options:
        print(option)
    res = input("")

    if res == "exit":
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


def findLines(regex, filePath):
    lines = getLines(filePath)

    if lines != None:
        matching = []

        i = 0
        for line in lines:
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


def fileIncludes(string, filePath):
    f = io.open(filePath, 'rt')
    lines = [line for line in f.readlines()]
    hasVal = False
    f.close()

    for line in lines:
        if string in line:
            hasVal = True

    return hasVal


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


def getEnv(name):
    lines = getLines('.env')
    for line in lines:
        a = re.findall(r"{}=([A-z]+)".format(name), line)
        if len(a) > 0:
            return a[0]
    print("print no env named \"{}\" found /_/".format(name))


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
            ("database/migrations/*{}s*.php".format(self.modelLower), "php artisan make:migration create_{}_table".format(self.table)),
            ("database/seeders/*{}*.php".format(self.modelLower), "php artisan make:seeder {}Seeder".format(self.model)),
            ("database/factories/*{}*.php".format(self.modelLower), "php artisan make:factory {}Factory".format(self.model))
        ]

        for file in files:
            if len(glob.glob(file[0])) == 0:
                command(file[1])

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



    def addSeed(self, name, option):
        if not fileIncludes("use Illuminate\\Support\\Facades\\DB;", self.seederPath):
            replace("use Illuminate\\\\Database\\\\Seeder;", "use Illuminate\\\\Database\\\\Seeder;\nuse Illuminate\\\\Support\\\\Facades\\\\DB;", self.seederPath)

        if not fileIncludes("insert\(\[", self.seederPath):
            replace("\/\/", "DB::table('{}')->insert([\n\t\t\t'created_at' => now()\n\t\t]);".format(self.table), self.seederPath)

        value = "''"
        if option == 'integer' or option == 'foreignId':
            value = 1
        

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

        if not fileIncludes(col, self.controllerPath):
            replace("::create\(\[", "::create([\n\t\t\t{col}".format(col = col), self.controllerPath)
            
            if option == 'file':
                replace("\${modelLower} = {model}::create\(\[".format(modelLower = self.modelLower, model = self.model), "$request->{name}->storePublicly('img', 'public');\n\n\t\t${modelLower} = {model}::create([".format(modelLower = self.modelLower, model = self.model, name = name), self.controllerPath)
        
        else:
            print("column already exists in store methode /_/")


    def addColumnToUpdate(self, name, option):
        if not fileIncludes("${}->save();".format(self.modelLower), self.controllerPath):
            print("to do : error handling addColumnToUpdate()")
            print("please report to the dev")
            print("thanks :)")

        if not fileIncludes("${modelLower}->{name} = ".format(modelLower = self.modelLower, name = name), self.controllerPath):
            col = "${modelLower}->{name} = $request->{name};".format(modelLower = self.modelLower, name = name)
            if option == 'file':
                col = "if ($request->{name}) {{\n\t\t\t${modelLower}->{name} = 'storage/img/'.$request->{name}->hashName();\n\t\t\t$request->{name}->storePublicly('img', 'public');\n\t\t}}".format(modelLower = self.modelLower, name = name)

            replace("\${}->save\(\);".format(self.modelLower), "{col}\n\t\t${modelLower}->save();".format(modelLower = self.modelLower, col = col), self.controllerPath)

        else:
            print("column already exists in update methode /_/")


    def addColumnToMigration(self, name, option):
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
            replace("{{-- toReplace --}}", '<form action="{{{{ route("{modelLower}.update", ${modelLower}) }}}}" method="POST" enctype="multipart/form-data">\n\t\t\t\t@csrf\n\t\t\t\t@method(\'PUT\')\n\t\t\t\t{{{{-- toReplace --}}}}'.format(modelLower = self.modelLower), self.editPath)

        inputType = "text"
        if option == "file":
            inputType = "file"

        if option == "file":
            index = "<td><img class=\"L-img\" src=\"{{{{ asset($item->{}) }}}}\"></img></td>".format(name)
        elif option == "foreignId":
            index = "<td>{{{{ $item->{}->id }}}}</td>".format(name.replace('_id', ''))
        else:
            index = "<td>{{{{ $item->{} }}}}</td>".format(name)

        if option == "foreignId" and subOption == "many":
            # create = 
            create = '<div class="mb-3 col-12 col-md-6">\n\t\t\t\t\t<label for="{name}" class="form-label">{nameUpper}</label>\n\t\t\t\t\t<input type={type} class="form-control" id="{name}" name="{name}">\n\t\t\t\t</div>'.format(name = name, nameUpper = name.capitalize(), type = inputType)
            edit = '<div class="mb-3 col-12 col-md-6">\n\t\t\t\t\t<label for="{name}" class="form-label">{nameUpper}</label>\n\t\t\t\t\t<input type={type} class="form-control" id="{name}" name="{name}" value="{{{{ ${modelLower}->{name} }}}}">\n\t\t\t\t</div>'.format(modelLower = self.modelLower, name = name, nameUpper = name.capitalize(), type = inputType)
        else:
            create = '<div class="mb-3 col-12 col-md-6">\n\t\t\t\t\t<label for="{name}" class="form-label">{nameUpper}</label>\n\t\t\t\t\t<input type={type} class="form-control" id="{name}" name="{name}">\n\t\t\t\t</div>'.format(name = name, nameUpper = name.capitalize(), type = inputType)
            edit = '<div class="mb-3 col-12 col-md-6">\n\t\t\t\t\t<label for="{name}" class="form-label">{nameUpper}</label>\n\t\t\t\t\t<input type={type} class="form-control" id="{name}" name="{name}" value="{{{{ ${modelLower}->{name} }}}}">\n\t\t\t\t</div>'.format(modelLower = self.modelLower, name = name, nameUpper = name.capitalize(), type = inputType)

        msg = []

        if not fileIncludes(index, self.indexPath):
            replace("<th>created_at<\/th>", "<th>{}</th>\n\t\t\t\t\t<th>created_at</th>".format(name.replace('_id', '').replace('_', ' ').capitalize()), self.indexPath)
            replace("{{-- toReplace --}}", "{}\n\t\t\t\t\t\t{{{{-- toReplace --}}}}".format(index), self.indexPath)
        else:
            msg.append("index")

        if not fileIncludes('<label for="{name}" class="form-label">{nameUpper}</label>'.format(name = name, nameUpper = name.capitalize()), self.createPath):
            replace("{{-- toReplace --}}", "{}\n\t\t\t\t{{{{-- toReplace --}}}}".format(create), self.createPath)
        else:
            msg.append("create")

        if not fileIncludes('<label for="{name}" class="form-label">{nameUpper}</label>'.format(name = name, nameUpper = name.capitalize()), self.editPath):
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
        if not fileIncludes("<a href=\"{{{{ route('{}.index') }}}}\">".format(self.modelLower), "resources/views/partials/backNavbar.blade.php") and self.inNavbar:
            replace("{{-- toReplace --}}", "<li>\n\t\t\t\t<a href=\"{{{{ route('{modelLower}.index') }}}}\">\n\t\t\t\t\t<i class='bx bx-grid-alt'></i>\n\t\t\t\t\t<span class=\"links_name\">{model}</span>\n\t\t\t\t</a>\n\t\t\t\t<span class=\"tooltip\">{model}</span>\n\t\t\t</li>\n\t\t\t{{{{-- toReplace --}}}}".format(modelLower = self.modelLower, model = self.model), "resources/views/partials/backNavbar.blade.php", 1)


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


    def addToWelcomeController(self):
        if not fileIncludes("'{}'".format(self.table), "app/Http/Controllers/WelcomeController.php"):
            replace("use Illuminate\\\\Http\\\\Request;", "use Illuminate\\\\Http\\\\Request;\nuse App\\\\Models\\\\{};".format(self.model), "app/Http/Controllers/WelcomeController.php")
            replace("index\(\) \{", "index() {{\n\t\t${} = {}::all();".format(self.table, self.model), "app/Http/Controllers/WelcomeController.php")
            replace("compact\(", "compact('{}',".format(self.table), "app/Http/Controllers/WelcomeController.php")


    def removeFromWelcomeController(self):
        deleteLineWhere("use App\\\\Models\\\\{};".format(self.model), "app/Http/Controllers/WelcomeController.php")
        deleteLineWhere("\${} = {}::all\(\);".format(self.table, self.model), "app/Http/Controllers/WelcomeController.php")
        replace("'{}',".format(self.table), "", "app/Http/Controllers/WelcomeController.php")

    def init(self):
        self.initController()
        self.initDatabaseSeeder()
        self.routes()
        self.initNavbar()
        self.addToWelcomeController()
        self.initModel()
        
        print("\nmodel {} initialized +__+\n".format(self.model))


    def addColumn(self, name, option="string", subOption=""):
        # migration / Seeder / Factory
        self.addColumnToMigration(name, option)
        self.addSeed(name, option)
        self.addColumnToFactory(name, option)

        # Controller
        self.addColumnToStore(name, option)
        self.addColumnToUpdate(name, option)
        self.addValidation(name)

        # Blades
        self.addColumnToBlades(name, option, subOption)

        print("column {} added -__-".format(name))


    def delete(self):
        files = [
            self.modelPath,
            self.controllerPath,
            self.migrationPath,
            self.seederPath,
            self.factoryPath,
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
        print(n)
        if len(n) > 0:
            deleteLines(n[0], n[0] + 1, "routes/web.php")

        n = findLines("Route::resource\('\/back\/{}', {}Controller::class\);".format(self.modelLower, self.model), "routes/web.php")
        if len(n) > 0:
            deleteLines(n[0], n[0] + 1, "routes/web.php")

        self.removeFromWelcomeController()

        print("\nmodel {} deleted :__:\n".format(self.model)) 



