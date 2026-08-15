from sqlalchemy.orm import Session
from university_catalog.database import get_engine, get_session_factory
from university_catalog.models import Department, Instructor, Course, Prerequisite, Base


def seed_database():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    try:
        existing_dept = session.query(Department).first()
        if existing_dept:
            print("Database already seeded, skipping...")
            return
        
        departments_data = [
            {"name": "Computer Science", "code": "CS"},
            {"name": "Artificial Intelligence & Machine Learning", "code": "AIML"},
            {"name": "Data Science", "code": "DS"},
            {"name": "Information Technology", "code": "IT"},
            {"name": "Mathematics", "code": "MATH"},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept = Department(**dept_data)
            session.add(dept)
            session.flush()
            departments[dept_data["code"]] = dept
        
        instructors_data = [
            {"name": "Dr. Alice Smith", "email": "alice.smith@university.edu", "office": "CS-101", "department_code": "CS"},
            {"name": "Dr. Bob Johnson", "email": "bob.johnson@university.edu", "office": "CS-202", "department_code": "CS"},
            {"name": "Dr. Carol Williams", "email": "carol.williams@university.edu", "office": "AIML-101", "department_code": "AIML"},
            {"name": "Dr. David Brown", "email": "david.brown@university.edu", "office": "DS-101", "department_code": "DS"},
            {"name": "Dr. Eva Martinez", "email": "eva.martinez@university.edu", "office": "IT-101", "department_code": "IT"},
            {"name": "Dr. Frank Chen", "email": "frank.chen@university.edu", "office": "MATH-101", "department_code": "MATH"},
            {"name": "Dr. Grace Lee", "email": "grace.lee@university.edu", "office": "AIML-202", "department_code": "AIML"},
            {"name": "Dr. Henry Davis", "email": "henry.davis@university.edu", "office": "DS-202", "department_code": "DS"},
        ]
        
        instructors = {}
        for inst_data in instructors_data:
            dept_code = inst_data.pop("department_code")
            inst = Instructor(**inst_data, department_id=departments[dept_code].id)
            session.add(inst)
            session.flush()
            instructors[inst.name] = inst
        
        courses_data = [
            {"course_code": "CS101", "title": "Introduction to Programming", "description": "A foundational course covering programming fundamentals, variables, control structures, functions, and basic data types using Python.", "credits": 3, "instructor": "Dr. Alice Smith", "department_code": "CS"},
            {"course_code": "CS102", "title": "Data Structures", "description": "Study of fundamental data structures including arrays, linked lists, stacks, queues, trees, and graphs with emphasis on algorithmic efficiency.", "credits": 3, "instructor": "Dr. Alice Smith", "department_code": "CS"},
            {"course_code": "CS201", "title": "Database Systems", "description": "Introduction to database design, relational models, SQL, normalization, transactions, and database management systems.", "credits": 3, "instructor": "Dr. Bob Johnson", "department_code": "CS"},
            {"course_code": "CS202", "title": "Object-Oriented Programming", "description": "Principles of object-oriented design including encapsulation, inheritance, polymorphism, and design patterns using Java.", "credits": 3, "instructor": "Dr. Bob Johnson", "department_code": "CS"},
            {"course_code": "CS301", "title": "Algorithms", "description": "Advanced algorithm design and analysis including sorting, searching, graph algorithms, dynamic programming, and NP-completeness.", "credits": 4, "instructor": "Dr. Alice Smith", "department_code": "CS"},
            {"course_code": "CS302", "title": "Operating Systems", "description": "Fundamentals of operating systems including processes, scheduling, memory management, file systems, and concurrency.", "credits": 4, "instructor": "Dr. Bob Johnson", "department_code": "CS"},
            {"course_code": "AIML201", "title": "Introduction to Artificial Intelligence", "description": "Overview of AI concepts including search algorithms, knowledge representation, reasoning, planning, and introduction to machine learning.", "credits": 3, "instructor": "Dr. Carol Williams", "department_code": "AIML"},
            {"course_code": "AIML301", "title": "Machine Learning", "description": "Comprehensive study of machine learning algorithms including supervised, unsupervised, and reinforcement learning with practical applications.", "credits": 4, "instructor": "Dr. Grace Lee", "department_code": "AIML"},
            {"course_code": "DS201", "title": "Statistics for Data Science", "description": "Statistical foundations for data science including probability, distributions, hypothesis testing, regression, and Bayesian inference.", "credits": 3, "instructor": "Dr. David Brown", "department_code": "DS"},
            {"course_code": "DS301", "title": "Data Mining", "description": "Techniques for discovering patterns in large datasets including classification, clustering, association rules, and anomaly detection.", "credits": 3, "instructor": "Dr. Henry Davis", "department_code": "DS"},
            {"course_code": "IT101", "title": "Information Technology Fundamentals", "description": "Introduction to IT concepts including hardware, software, networking, security, and system administration basics.", "credits": 3, "instructor": "Dr. Eva Martinez", "department_code": "IT"},
            {"course_code": "IT201", "title": "Network Administration", "description": "Design, implementation, and management of computer networks including routing, switching, wireless, and network security.", "credits": 3, "instructor": "Dr. Eva Martinez", "department_code": "IT"},
            {"course_code": "MATH101", "title": "Calculus I", "description": "Differential calculus including limits, derivatives, applications of differentiation, and introduction to integration.", "credits": 4, "instructor": "Dr. Frank Chen", "department_code": "MATH"},
            {"course_code": "MATH201", "title": "Linear Algebra", "description": "Vector spaces, linear transformations, eigenvalues, eigenvectors, and applications to computer science and data science.", "credits": 3, "instructor": "Dr. Frank Chen", "department_code": "MATH"},
            {"course_code": "MATH301", "title": "Discrete Mathematics", "description": "Logic, set theory, combinatorics, graph theory, and mathematical proofs with applications to computer science.", "credits": 3, "instructor": "Dr. Frank Chen", "department_code": "MATH"},
        ]
        
        courses = {}
        for course_data in courses_data:
            instructor_name = course_data.pop("instructor")
            dept_code = course_data.pop("department_code")
            course = Course(
                **course_data,
                instructor_id=instructors[instructor_name].id,
                department_id=departments[dept_code].id,
            )
            session.add(course)
            session.flush()
            courses[course_data["course_code"]] = course
        
        prerequisites_data = [
            ("CS102", "CS101"),
            ("CS201", "CS101"),
            ("CS202", "CS101"),
            ("CS301", "CS102"),
            ("CS302", "CS202"),
            ("AIML301", "AIML201"),
            ("AIML301", "CS201"),
            ("DS301", "DS201"),
            ("DS301", "CS201"),
            ("IT201", "IT101"),
            ("MATH201", "MATH101"),
            ("MATH301", "MATH101"),
        ]
        
        for course_code, prereq_code in prerequisites_data:
            course = courses[course_code]
            prereq = courses[prereq_code]
            prereq_rel = Prerequisite(course_id=course.id, prerequisite_id=prereq.id)
            session.add(prereq_rel)
        
        session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()