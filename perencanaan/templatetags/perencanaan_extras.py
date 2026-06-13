from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    request = context.get("request")
    if not request:
        return ""
    q = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == "" or value == "semua":
            q.pop(key, None)
        else:
            q[key] = value
    return q.urlencode()
