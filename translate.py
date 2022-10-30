import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--input",help="cucumber steps java file folder",required=True)
parser.add_argument("--output",help="robotframework library folder",required=True)
args = parser.parse_args()

if __name__ == "__main__":
    input_dir = args.input
    output_dir = args.output
    files = os.listdir(input_dir)
    java_files = [file for file in files if file.endswith(".java")]
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    init_txt = ""

    utils_txt = """
def convert_datatable(datalist):
    from io.cucumber.datatable import DataTable
    res =[]
    row = []
    for item in datalist:
        if item == "::":
            res.append(row)
            row = []
        else:
            row.append(item)
    return DataTable.create(res)
    """

    for java_file in java_files:
        py_text = ""
        robot_text = ""
        lines = open(input_dir+"/"+java_file,"r",encoding="utf-8").readlines()
        cls_name = java_file.split(".")[0]
        is_step = False
        for line in lines:
            if line.find("package ")>=0:
                py_text += line.strip(";\n").replace("package ", "from ") + " import " + cls_name + "\n"
                py_text += "from .utils import *\n\n\n"
                py_text += cls_name.lower() + " = " + cls_name + "()" + "\n"
            if line.find("@Then") >= 0 or line.find("@Given") >= 0 or line.find("@And") >= 0 or line.find("@When") >= 0 or line.find("@But"):
                is_step = True

            if is_step:
                if line.find("public void ") >= 0 or line.find("public static void ") >= 0:
                    header = cls_name.lower()
                    func = line.strip(" \n").rsplit(")")[0].split(" ",2)[2]
                    if line.find("public static void ") >= 0 :
                        header = cls_name
                        func = line.strip(" \n").rsplit(")")[0].split(" ",3)[3]

                    func_name,arguments = func.split("(")
                    arg_list = arguments.split(",")
                    datatable = False
                    args = []
                    j_args = []
                    table_arg = ""
                    for arg in arg_list:
                        if arg.find(" ") >= 0:
                            arg_name = arg.strip(" ").rsplit(" ",1)[1]
                            args.append(arg_name)
                            if arg.find("DataTable") >= 0:
                                datatable = True
                                table_arg = arg_name
                                j_args.append("py_" + table_arg)
                            else:
                                j_args.append(arg_name)
                    py_text += "\n\n" + "def " + func_name + "(" + ",".join(args) + "):\n"
                    if datatable:
                        py_text += "\tpy_" + table_arg + " = convert_datatable(" + table_arg +")\n"
                    py_text += "\t" + header + "." + func_name + "(" + ",".join(j_args) + ")\n"
                    is_step = False

        py_file = open(output_dir+ "/" + cls_name + ".py", "w")
        py_file.write(py_text)
        py_file.close()
        init_txt +="from ."+ cls_name + " import *\n"

    init_file = open(output_dir + "/__init__.py","w")
    init_file.write(init_txt)
    init_file.close()
    utils_file = open(output_dir + "/utils.py","w")
    utils_file.write(utils_txt)
    utils_file.close()


