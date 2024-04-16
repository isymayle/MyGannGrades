import re
import PyPDF2

from config import first_semester_path, second_semester_path, is_printing


#returns text from pdf given in pdf_path
def extract_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

#divide numbers in two parentheses using re.search and a pattern
def divide_numbers_in_parentheses(line):
    # Use regular expression to find numbers inside parentheses
    grade_pattern = r'(\d+(\.\d+)?)\s*\((\d+(\.\d+)?)\)'
    matches = re.search(grade_pattern, line)
    if matches:
        # Extract numbers from the matches
        num1 = float(matches.group(1))
        num2 = float(matches.group(3))
        
        # Perform division
        result = round(100*num1 / num2, 2)
        return result  # Return the result instead of printing
    else:
        return None  # Return None if no match is found

#find grade pattern add it to matchess
def find_matches_grade_pattern(line):
        # Use regular expression to find numbers inside parentheses
    grade_pattern = r'(\d+(\.\d+)?)\s*\((\d+(\.\d+)?)\)'
    grade_object = re.search(grade_pattern, line)
    if grade_object:
        return (grade_object.group(0))

#with 2 numbers on numerator and denominator divide numbers in parentheses using re.search and a pattern
def divide_two_numbers_in_parentheses(grade_line1,grade_line2):
    pattern = r'(\d+(\.\d+)?)\s*\((\d+(\.\d+)?)\)'
    matches1 = re.search(pattern, grade_line1)
    matches2 = re.search(pattern, grade_line2)
    if matches1:
        # Extract numbers from the matches
        num1a = float(matches1.group(1))
        num1b = float(matches1.group(3))
        num2a = float(matches2.group(1))
        num2b = float(matches2.group(3))
        
        # Perform division
        result = round(100*(num1a+num2a) / (num1b+num2b), 2)
        return result  # Return the result instead of printing
    else:
        return None  # Return None if no match is found
    

def out_of_full_year(grade_line1,grade_line2):
    pattern = r'(\d+(\.\d+)?)\s*\((\d+(\.\d+)?)\)'
    matches1 = re.search(pattern, grade_line1)
    matches2 = re.search(pattern, grade_line2)
    if matches1:
        # Extract numbers from the matches
        num1a = float(matches1.group(1))
        num1b = float(matches1.group(3))
        num2a = float(matches2.group(1))
        num2b = float(matches2.group(3))
        
        # Perform division
        result = (num1a+num2a)
        result2 = (num1b+num2b)
        return f"{result} / {result2}" # Return the result instead of printing
    else:
        return None  # Return None if no match is found


#find lettergrade by putting together plus-minus grade and int-score
def letter_grader(score):
    def plus_minus_grade(score):
        int_score = int(score/10)
        fractional_score = score % 10
        if int_score == 10:
            return "+"
        elif int_score < 6:
            return ""
        elif fractional_score >= 7:
            return "+"
        elif fractional_score >= 3:
            return ""
        else:
            return "-"
    if score is not None:  # Check if score is None
        int_score = int(score/10)
        if int_score == 10:
            int_score = 9
        if int_score < 5:
            int_score = 5
        letter_array = ['A', 'B', 'C', 'D', 'F']
        return( letter_array[9 - int_score] + plus_minus_grade(score))  # Concatenate strings without space
    else:
        return( "no grade input")  # Handle case where score is None

#associate class names with grades in gievn pdf, and put into dictionary grades_with_names
def pdf_class_names_grades(pdf_path, pattern):
    pdf_text = extract_text(pdf_path)
    grades_with_names = {}
    class_names = []
    lines = pdf_text.split('\n') 
    for i, line in enumerate(lines):
        name_line = re.search(pattern, line)
        if name_line:
            #block = name_line.group(1)[0]
            string = re.search(r'([^(\d]+)', line)
            class_name = string.group(1).strip()
            if class_name not in class_names:
                class_names.append(class_name)
            index = lines.index(line)
            #print(f"class name: {class_name} index {index}")
            next_line = lines[index + 1]
            #print(f"next line {next_line}")
            next_next_line = lines[index + 2]
            if (find_matches_grade_pattern(next_line)):
                grade_line = find_matches_grade_pattern(next_line)
                #print(f"found on first line {grade_line}")
            else:
                grade_line = find_matches_grade_pattern(next_next_line)
                #print(f"found on second line {grade_line}")
            #print("1st - " + block1 + " - "+class_name1)
            grades_with_names[class_name] = grade_line
    return grades_with_names


def find_associated_lines(pdf_path1, pdf_path2, printing=bool):
    pattern = re.compile(r'([A-E] - [A-Z]{2})') 
    printed_class_names = []

    grades_with_names1 = pdf_class_names_grades(pdf_path1, pattern)  
    grades_with_names2 = pdf_class_names_grades(pdf_path2, pattern)  

    #print(pattern)
    #print(grades_with_names1)
    #print(grades_with_names2)

    all_class_data = []
    #full year classes
    for class_name1, grade1 in grades_with_names1.items():
        if class_name1 in grades_with_names2:
            class_data = {}
            class_data["class_name"] = class_name1 #adds class name to class data
            if printing==True:
                print(class_name1)
            grade2 = grades_with_names2[class_name1]
            if printing==True:
                print(grade1 + ", " + grade2)
                print(out_of_full_year(grade1, grade2))
            class_data["points_grade"] = grade1 + ", " + grade2 #adds percent grade to class data
            result = divide_two_numbers_in_parentheses(grade1, grade2)
            if printing==True:
                print(result, "%", sep='')
            class_data["percent_grade"] = result #adds percent grade to class data
            letter_grade = letter_grader(result)
            if printing==True:
                print(letter_grade)
            class_data["letter_grade"] = letter_grade #adds percent grade to class data
            printed_class_names.append(class_name1)
            if printing==True:
                print()
            all_class_data.append(class_data) #adds to all class data list
                
    #single semester 1
    for class_name,grade in grades_with_names1.items():
        if class_name not in printed_class_names:
            class_data = {}
            if printing==True:
                print(class_name)
            class_data["class_name"] = class_name #adds class name to class data
            if printing==True:
                print(grade)
            class_data["points_grade"] = grade #adds percent grade to class data
            if printing==True:
                print(divide_numbers_in_parentheses(grade),"%",sep='')
            class_data["percent_grade"] =  divide_numbers_in_parentheses(grade) #adds percent grade to class data
            if printing==True:
                print(letter_grader(divide_numbers_in_parentheses(grade)))
            class_data["letter_grade"] =  letter_grader(divide_numbers_in_parentheses(grade)) #adds letter grade to class data
            printed_class_names.append(class_name)
            print ()
            all_class_data.append(class_data) #adds to all class data list
    #single semester 2
    for class_name,grade in grades_with_names2.items():
        if class_name not in printed_class_names:
            class_data = {}
            if printing==True:
                print(class_name)
            class_data["class_name"] = class_name #adds class name to class data
            if printing==True:
                print(grade)
            class_data["points_grade"] = grade #adds percent grade to class data
            if printing==True:
                print(divide_numbers_in_parentheses(grade),"%",sep='')
            class_data["percent_grade"] =  divide_numbers_in_parentheses(grade) #adds percent grade to class data
            if printing==True:
                print(letter_grader(divide_numbers_in_parentheses(grade)))
            class_data["letter_grade"] =  letter_grader(divide_numbers_in_parentheses(grade)) #adds letter grade to class data
            printed_class_names.append(class_name1)
            print ()
            all_class_data.append(class_data) #adds to all class data list
    return all_class_data
    

def data_grades():
    pdf_path1 = first_semester_path
    pdf_path2 = second_semester_path
    class_data = find_associated_lines(pdf_path1, pdf_path2, printing=is_printing)
    return class_data
