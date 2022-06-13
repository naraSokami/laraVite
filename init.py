import os
import shutil
import utils as u
import glob
from relationships import *
import time
from env import *

def initRolesSystem():
    # model
    if len(glob.glob("app\\Models\\Role.php")) == 0:
        os.system("php artisan make:model Role")

    # migration
    if len(glob.glob("database\\migrations\\*create_roles_table.php")) == 0:
        os.system("php artisan make:migration create_roles_table")

    if not u.fileIncludes("$table->string('name');", glob.glob("database\\migrations\\*create_roles_table.php")[0]):
        u.replace("\$table->id\(\);", "$table->id();\n\t\t\t$table->string('name');", glob.glob("database\\migrations\\*create_roles_table.php")[0])

    # seeder
    if len(glob.glob("database\\seeders\\RoleSeeder.php")) == 0:
        os.system("php artisan make:seeder RoleSeeder")

    u.replace("\/\/", "DB::table('roles')->insert([\n\t\t\t'name' => 'user',\n\t\t]);\n\n\t\tDB::table('roles')->insert([\n\t\t\t'name' => 'admin',\n\t\t]);", "database\\seeders\\RoleSeeder.php")
    u.use("Illuminate\\Support\\Facades\\DB", "database\\seeders\\RoleSeeder.php")

    if not u.fileIncludes("RoleSeeder::class,", "database/seeders/DatabaseSeeder.php"):
        u.replace("\$this->call\(\[", "$this->call([\n\t\t\tRoleSeeder::class,", "database/seeders/DatabaseSeeder.php")

    # relashionship
    userModel = u.Empty()
    userModel.model = "User"
    userModel.modelLower = "user"
    userModel.migrationPath = glob.glob("database\\migrations\\*_create_users_table.php")[0]
    userModel.modelPath = "app\\Models\\User.php"
    userModel.table = "users"

    roleModel = u.Empty()
    roleModel.model = "Role"
    roleModel.modelLower = "role"
    roleModel.modelPath = "app\\Models\\Role.php"
    roleModel.migrationPath = glob.glob("database\\migrations\\*create_roles_table.php")[0]
    # userModel.factoryPath = "database\\factories\\UserFactory.php"
    userModel.controllerPath = "app\\Http\\Controllers\\Auth\\RegisteredUserController.php"

    hasMany(roleModel, userModel)
    belongsTo(roleModel, userModel)
    avoidIntegrityConstraintViolation(roleModel, userModel)

    # migration / seeder
    u.Model.addColumnToMigration(userModel, "role_id", "foreignId")
    u.replace("foreignId\('role_id'\)->nullable\(\)", "foreignId('role_id')->default(1)", userModel.migrationPath)
    # u.Model.addColumnToFactory(userModel, "role_id", "foreignId")

    # Controller
    u.Model.addColumnToStore(userModel, "role_id", "foreignId")

    print("roles system initialized +__+")
    

def initEnv():
    u.addEnv("LARAVITE_AUTO_MIGRATE", "True")
    u.addEnv("LARAVITE_INIT", "True") 

    envs = [
        MAIL_MAILER,
        MAIL_HOST,
        MAIL_PORT,
        MAIL_USERNAME,
        MAIL_PASSWORD,
        MAIL_ENCRYPTION,
    ]

    for env in envs:
        if not u.isEnv(u.varname(env)):
            u.addEnv(u.varname(env), env)
        else:
            u.setEnv(u.varname(env), env)


def init():

    # Database
    dbPort = ""
    dbName = input("\nwhat's the name of your database ?\n")

    if os.name == 'posix':
        dbPort = 8889
    else:
        dbPort = 3306        

    u.replace("DB_PORT=3306", "DB_PORT={}".format(dbPort), ".env")
    u.replace("DB_DATABASE=laravel", "DB_DATABASE=\"{}\"".format(dbName), ".env")
    

    # Installation
    os.system("composer require laravel/ui")
    os.system("php artisan ui bootstrap")
    os.system("npm install")
    os.system("npm run dev")


    # Authentication
    res = u.ask("Add authentication system ? [y/n]", ["y", "n"])
    
    if res == "y":
        
        res = u.ask("Please choose one:", ["1", "2"], ["1) Breeze", "2) Coming soon..."])
        if res == "1":
            os.system("composer require laravel/breeze --dev")
            os.system("php artisan breeze:install")
            os.system("npm install && npm run dev")
            os.system("php artisan migrate")
            
            if not u.fileIncludes(".sass('resources/sass/app.scss', 'public/css')", "webpack.mix.js"):
                n = u.findLines(";", "webpack.mix.js")
                if len(n) > 0:
                    u.replace(";", "\n.sass('resources/sass/app.scss', 'public/css')\n.sourceMaps();", "webpack.mix.js", 1, n[len(n) - 1])

            if u.fileIncludes("/dashboard", "app/Providers/RouteServiceProvider.php"):
                u.replace("/dashboard", "/", "app/Providers/RouteServiceProvider.php", 1)
            
        elif res == "2":
            print("coming soon...")


    # DatabaseSeeder
    n = u.findLines("{", "database/seeders/DatabaseSeeder.php")[1]
    print(n)
    lines = u.addLines(["\t\t$this->call([\n", "\n", "\t\t]);\n", "\n"], "database/seeders/DatabaseSeeder.php", n)
    u.write("database/seeders/DatabaseSeeder.php", "".join(lines))
    

    # ask if add roles system
    res = u.ask("Add roles system ? [y/n]", ["y", "n"])
    if res == "y":
        initRolesSystem()
    
        
    for dir in ["back", "pages"]:
        if not os.path.isdir("resources/views/{}".format(dir)):
            os.mkdir("resources/views/{}".format(dir))
    for dir in ["layouts", "partials"]:
        if not os.path.isdir("resources/views/{}".format(dir)):
            shutil.copytree(os.path.dirname(__file__) + '\\{}'.format(dir), "resources/views/{}".format(dir))
        else:
            for file in os.listdir("{}/{}".format(os.path.dirname(__file__), dir)):
                if not os.path.isfile("resources/views/{}/{}".format(dir, file)):
                    print(file)
                    shutil.copy("{}/{}/{}".format(os.path.dirname(__file__), dir, file), "resources/views/{}".format(dir))

    if not os.path.isfile("public/css/L.css"):
        shutil.copy("{}/css/L.css".format(os.path.dirname(__file__)), "public/css")


    # Routes
    n = u.findLines("Route::get\('\/', function \(\) {", "routes/web.php")
    u.deleteLines(n[0], n[0] + 3, "routes/web.php")

    lines = u.addLines(["Route::get('/', [WelcomeController::class, 'index']);\n", "Route::view('/back', 'layouts.back');\n"], "routes/web.php", n[0] - 1)
    u.write("routes/web.php", "".join(lines))
    u.replace("use Illuminate\\\\Support\\\\Facades\\\\Route;", "use Illuminate\\\\Support\\\\Facades\\\\Route;\nuse App\\\\Http\\\\Controllers\\\\WelcomeController;", "routes/web.php")


    # Welcome
    os.system("php artisan make:controller WelcomeController")
    shutil.move("resources/views/welcome.blade.php", "resources/views/pages/welcome.blade.php")
    u.replace("\/\/", "function index()\n\t{\n\t\treturn view('pages.welcome', compact());\n\t}", "app/Http/Controllers/WelcomeController.php")


    # Storage
    os.system("php artisan storage:link")

    # Eventualy
    os.system("npm run dev")
    print("\nmake sure to \"npm run dev\" until")
    print("u see the \"build successful\" notif")
    print("if u didn't received it just now")

    # Env
    initEnv()

    print("\nInitialization complete !")   
    return 0


def isInitialized():
    if u.fileIncludes("LARAVITE_INIT=True", ".env"):
        return True
    return False


# init()