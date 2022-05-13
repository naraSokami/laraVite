import os
import utils as u


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


def avoidIntegrityConstraintViolationInMigrations(model, otherModel):
    modelFileN = model.migrationPath.replace("database\\migrations\\", "").split("_")
    otherModelFileN = otherModel.migrationPath.replace("database\\migrations\\", "").split("_")

    while int(modelFileN[0]) >= int(otherModelFileN[0]):
        modelFileN[0] = int(modelFileN[0]) - 1

    modelFileN[0] = str(modelFileN[0])
    newPath = "database\\migrations\\" + "_".join(modelFileN)

    os.rename(model.migrationPath, newPath)
    model.migrationPath = newPath


def avoidIntegrityConstraintViolationInSeeder(model, otherModel):
    n = u.findLines("{}Seeder::class".format(model.model), "database/seeders/DatabaseSeeder.php")
    m = u.findLines("{}Seeder::class".format(otherModel.model), "database/seeders/DatabaseSeeder.php")

    if len(n) > 0 and len(m) > 0:
        if n[0] > m[0]:
            u.switchLines(n[0], m[0], "database/seeders/DatabaseSeeder.php")


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
    

def oneToMany(model , otherModel):
    # addColumn
    otherModel.addColumn("{}_id".format(model.modelLower), "foreignId", "one_to_many")
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
