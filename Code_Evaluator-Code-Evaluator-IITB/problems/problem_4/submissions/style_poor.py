def evaluate_expression(s: str) -> int:
 x=0;n=len(s)
 def e():
  nonlocal x
  r=t()
  while x<n:
   if s[x]==' ':x+=1;continue
   if s[x]=='+':x+=1;r+=t()
   elif s[x]=='-':x+=1;r-=t()
   else:break
  return r
 def t():
  nonlocal x
  r=f()
  while x<n:
   if s[x]==' ':x+=1;continue
   if s[x]=='*':x+=1;r*=f()
   elif s[x]=='/':
    x+=1;d=f();r=int(r/d)
   else:break
  return r
 def f():
  nonlocal x
  while x<n and s[x]==' ':x+=1
  if s[x]=='(':
   x+=1;r=e()
   while x<n and s[x]==' ':x+=1
   x+=1;return r
  nn=0
  while x<n and s[x].isdigit():nn=nn*10+int(s[x]);x+=1
  return nn
 return e()
