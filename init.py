from dataclasses import replace
import os
import shutil
import utils as u

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
            
        elif res == "2":
            print("coming soon...")

        
    # Tree (error handling: ok)
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
    u.replace("\/\/", "function index() {\n\t\treturn view('pages.welcome', compact());\n\t}", "app/Http/Controllers/WelcomeController.php")


    # DatabaseSeeder
    n = u.findLines("{", "database/seeders/DatabaseSeeder.php")[1]
    print(n)
    lines = u.addLines(["\t\t$this->call([\n", "\n", "\t\t]);\n", "\n"], "database/seeders/DatabaseSeeder.php", n)
    u.write("database/seeders/DatabaseSeeder.php", "".join(lines))


    # Storage
    os.system("php artisan storage:link")

    # Eventualy
    os.system("npm run dev")
    print("\nmake sure to \"npm run dev\" until")
    print("u see the \"build successful\" notif")
    print("if u didn't received it just now")

    # Env
    u.addEnv("LARAVITE_AUTO_MIGRATE", "True")
    u.addEnv("LARAVITE_INIT", "True")

    print("\nInitialization complete !")    

    return 0


def isInitialized():
    if u.fileIncludes("LARAVITE_INIT=True", ".env"):
        return True
    return False


# init()