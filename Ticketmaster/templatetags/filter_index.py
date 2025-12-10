from django import template

register = template.Library()

def index(value, arg):
    return value[arg]