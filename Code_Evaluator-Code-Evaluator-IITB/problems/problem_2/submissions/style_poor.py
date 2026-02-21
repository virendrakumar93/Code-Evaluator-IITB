def generate_parentheses(n: int) -> list[str]:
    if n==0:return [""]
    r=[]
    def f(s,o,c):
        if len(s)==2*n:r.append(s);return
        if o<n:f(s+"(",o+1,c)
        if c<o:f(s+")",o,c+1)
    f("",0,0)
    return r
