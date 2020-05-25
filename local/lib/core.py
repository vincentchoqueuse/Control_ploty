import os
import boto3
from jinja2 import Environment, FileSystemLoader
from .filters import *

class Jinja_Mixin():
    
    template_folder = "./templates"

    def get_template(self):
        file_loader = FileSystemLoader(self.template_folder)
        env = Environment(loader=file_loader)
        env.filters["moodle_numerical"] = moodle_numerical
        env.filters["moodle_filter_type"] = moodle_filter_type
        return env.get_template(self.get_template_name())
    
    def get_template_name(self):
        template_name = self.template_name
        if template_name is None:
            template_name = "{}.xml".format(self.name)
        return template_name

    def render(self):
        template = self.get_template()
        context = self.get_context_data()
        xml = template.render(**context)
        self.xml = xml
        return xml


class Quiz(Jinja_Mixin):
    
    template_name = "quiz.xml"

    def __init__(self,name,text=""):
        self.name = name
        self.object_list = []
        self.text = text
        self.xml = None
    
    def add(self,category):
        self.object_list.append(category)
    
    def get_context_data(self):
        context = {}
        context["name"] = self.name
        context["object_list"] = self.object_list
        return context
    
    def render(self):
        template = self.get_template()
        context = self.get_context_data()
        xml = template.render(**context)
        self.xml = xml
        return xml
    
    def save(self,filename):

        file = open(filename, "w")
        file.write(self.xml)
        file.close()


class Category(Jinja_Mixin):
    
    template_name = "category.xml"

    def __init__(self,name,text=""):
        self.name = name
        self.object_list = []
        self.text = text

    def add(self,question):
        self.object_list.append(question)
    
    def get_context_data(self):
        context = {}
        context["name"] = self.name
        context["object_list"] = self.object_list
        return context

class Question(Jinja_Mixin):
    
    name = None
    template_name = None

    def __init__(self,object,name = "temp",text=""):
        self.object = object
        self.name = name
        self.text = text
    
    def get_context_data(self):
        # override this method if needed
        context = {}
        context["name"] = self.name
        context["object"] = self.object
        return context
