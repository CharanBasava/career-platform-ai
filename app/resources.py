def get_resources(missing_skills):
    """
    Acts as a resource API to map skill gaps to official documentation 
    and video masterclasses.
    """
    # Your verified high-priority mappings
    official_docs = {
        "python": "https://docs.python.org/3/",
        "sql": "https://dev.mysql.com/doc/",
        "hadoop": "https://hadoop.apache.org/docs/stable/",
        "spark": "https://spark.apache.org/docs/latest/",
        "aws": "https://aws.amazon.com/free/",
        "docker": "https://docs.docker.com/",
        "kubernetes": "https://kubernetes.io/docs/home/",
        "tableau": "https://help.tableau.com/current/pro/desktop/en-us/gettingstarted_office.htm",
        "power bi": "https://learn.microsoft.com/en-us/power-bi/",
        "machine learning": "https://scikit-learn.org/stable/user_guide.html",
        "deep learning": "https://www.tensorflow.org/learn",
        "git": "https://git-scm.com/doc"
    }

    resource_list = []
    
    for skill in missing_skills:
        skill_clean = skill.lower().strip()
        
        # API Logic: If skill is in our verified list, use it; 
        # otherwise, generate a dynamic search link.
        doc_link = official_docs.get(
            skill_clean, 
            f"https://www.google.com/search?q={skill_clean}+official+documentation+docs"
        )
        
        resource_list.append({
            "skill": skill.title(),
            "doc": doc_link,
            "coursera": f"https://www.coursera.org/courses?query={skill_clean}",
            "youtube": f"https://www.youtube.com/results?search_query={skill_clean}+full+course+masterclass"
        })
        
    return resource_list