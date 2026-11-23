"""Built-in skills list for extraction and matching.

Each entry is a canonical skill name with the spellings that count as
the same skill. The list is not exhaustive — the README says so — but
it covers the common tech, business and soft skills in the jobs this
tool is used for.
"""

# canonical name -> spellings that count as that skill
SKILLS = {
    # --- Programming and tech ---
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "C++": ["c++"],
    "C#": ["c#", "c sharp"],
    "SQL": ["sql", "mysql", "postgresql", "postgres"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Django": ["django"],
    "Flask": ["flask"],
    "React": ["react", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Git": ["git", "github", "gitlab"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Natural Language Processing": ["natural language processing", "nlp"],
    "Computer Vision": ["computer vision"],
    "REST API": ["rest api", "restful api", "rest apis"],
    "Linux": ["linux"],
    "Excel": ["excel", "microsoft excel", "ms excel"],
    "Power BI": ["power bi"],
    "Tableau": ["tableau"],
    "WordPress": ["wordpress"],
    "Flutter": ["flutter"],
    "Android": ["android"],
    "iOS": ["ios"],
    "Figma": ["figma"],
    "Photoshop": ["photoshop", "adobe photoshop"],
    "Cybersecurity": ["cybersecurity", "cyber security"],
    "Networking": ["networking"],
    "Testing": ["testing", "unit testing", "qa testing"],
    "Agile": ["agile", "scrum"],
    "DevOps": ["devops"],
    # --- Business ---
    "Project Management": ["project management"],
    "Digital Marketing": ["digital marketing"],
    "SEO": ["seo", "search engine optimisation", "search engine optimization"],
    "Social Media Marketing": ["social media marketing"],
    "Content Writing": ["content writing"],
    "Accounting": ["accounting"],
    "Bookkeeping": ["bookkeeping"],
    "Sales": ["sales"],
    "Customer Service": ["customer service"],
    "Business Analysis": ["business analysis"],
    "Data Entry": ["data entry"],
    "Supply Chain": ["supply chain"],
    "Human Resources": ["human resources", "hr"],
    "Finance": ["finance", "financial analysis"],
    "Teaching": ["teaching", "training", "tutoring"],
    # --- Soft skills ---
    "Communication": ["communication", "communication skills"],
    "Teamwork": ["teamwork", "team work", "collaboration"],
    "Leadership": ["leadership", "team lead", "team leadership"],
    "Problem Solving": ["problem solving"],
    "Time Management": ["time management"],
    "Adaptability": ["adaptability", "adaptable"],
    "Creativity": ["creativity", "creative thinking"],
    "Attention to Detail": ["attention to detail", "detail oriented"],
    "Public Speaking": ["public speaking"],
    "Negotiation": ["negotiation"],
    "Critical Thinking": ["critical thinking"],
}

ALL_SKILLS = list(SKILLS.keys())


def skill_variants(skill):
    """Return the spellings that count as this skill."""
    return SKILLS.get(skill, [skill.lower()])
