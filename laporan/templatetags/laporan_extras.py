from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def laporan_query(context, **kwargs):
    """Bangun query string GET dengan override; reset halaman saat filter berubah."""
    request = context.get("request")
    if not request:
        return ""
    q = request.GET.copy()
    q.pop("page", None)
    for key, value in kwargs.items():
        if value is None or value == "" or value == "semua":
            q.pop(key, None)
        else:
            q[key] = value
    return q.urlencode()


@register.filter
def initials(nama):
    parts = (nama or "").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (nama[:2].upper() if nama else "??")


@register.filter
def jurusan_badge_class(kode):
    kode = (kode or "").upper()
    if kode == "DKV":
        return "bg-violet-50 text-violet-700"
    if kode == "RPL":
        return "bg-blue-50 text-blue-700"
    return "bg-navy-50 text-navy-700"
