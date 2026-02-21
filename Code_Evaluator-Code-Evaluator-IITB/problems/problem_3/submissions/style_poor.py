def climb_stairs(n:int)->int:
 x=1;y=2
 if n<=2:return n
 for z in range(3,n+1):
  q=x+y;x=y;y=q
 return y
