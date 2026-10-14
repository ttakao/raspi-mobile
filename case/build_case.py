import sys
import trimesh as t
import numpy as np
from pathlib import Path
out=Path(__file__).resolve().parent
out.mkdir(parents=True,exist_ok=True)
def box(size,pos):
 m=t.creation.box(extents=size);m.apply_translation(np.array(pos)+np.array(size)/2);return m
def rounded(w,h,z,r,base=0):
 ms=[]
 for x,y in [(r,r),(w-r,r),(w-r,h-r),(r,h-r)]:
  m=t.creation.cylinder(radius=r,height=z,sections=32);m.apply_translation([x,y,base+z/2]);ms.append(m)
 return t.boolean.union(ms + [box([w-2*r,h,z],[r,0,base]),box([w,h-2*r,z],[0,r,base])],engine="manifold")
def cut(a,b):return t.boolean.difference([a,b],engine='manifold')
def union(ms):return t.boolean.union(ms,engine='manifold')
def cylx(rad,length,x,y,z,sections=40):
 m=t.creation.cylinder(radius=rad,height=length,sections=sections);m.apply_transform(t.transformations.rotation_matrix(np.pi/2,[0,1,0]));m.apply_translation([x+length/2,y,z]);return m
# Front view: x left->right; y bottom->top. Front exterior z=0.
# Internal 90x90x33; outer 94x94x37 including 2mm back lid.
body=cut(rounded(94,94,35,3),box([90,90,34],[2,2,2]))
# LCD/window placement mirrored in x from the original V4 (2026-10-14).
body=cut(body,box([75,50,4],[11.5,38,-1]))
# Top pair of side screws only.
for x in [-1,89]:
 body=cut(body,cylx(1.7,6,x,84,31))
# Switch side mirrored from original V4; y/z remain unchanged.
body=cut(body,cylx(2.4,5,-1,74,18))
# Lower receivers, open toward upper edge; 10.8 wide x 2.4 high slots.
for x in [22,62]:
 receiver=box([14.8,7,6.2],[x-2.4,2,28.8])
 receiver=cut(receiver,box([10.8,6,2.4],[x-.4,3.5,30.8]))
 body=union([body,receiver])
# Lid: partial lip (no bottom rail) permits insertion before closing.
lid=rounded(94,94,2,3,35)
parts=[lid,
 box([2,80,3],[2.4,10,32]),box([2,80,3],[89.6,10,32]),
 box([89.2,2,3],[2.4,89.6,32])]
for x in [2.4,83.6]:
 parts.append(box([8,9,8],[x,79.5,27]))
# 2mm tongues with generous roots. Ends y4..10 enter lower receivers.
for x in [22,62]:
 parts += [box([10,8,2],[x,4,31]),box([10,4,4],[x,10,31])]
lid=union(parts)
for x in [-1,83]:lid=cut(lid,cylx(1.7,12,x,84,31))
for x in [7.4,83.6]:lid=cut(lid,cylx(5.8/np.sqrt(3),3.1,x,84,31,6))
# Collision audit in the closed position, before changing print orientation.
inter=t.boolean.intersection([body,lid],engine='manifold')
assert abs(inter.volume)<1e-5, inter.volume
print('Closed assembly interference volume:',inter.volume)
lid.apply_transform(t.transformations.rotation_matrix(np.pi,[1,0,0]));lid.apply_translation(-lid.bounds[0])
for name,m in [('ssh_case_v4_body',body),('ssh_case_v4_lid',lid)]:
 assert m.is_watertight and m.volume>0
 # Check one connected component without optional scipy/networkx.
 parent=list(range(len(m.vertices)))
 def root(a):
  while parent[a]!=a:
   parent[a]=parent[parent[a]];a=parent[a]
  return a
 for a,b in m.edges:
  a,b=root(int(a)),root(int(b));parent[a]=b
 assert len({root(i) for i in range(len(parent))})==1
 if '--body-only' not in sys.argv or name.endswith('_body'):
  m.export(out/(name+'.stl'))
 print(name,m.extents,'watertight',m.is_watertight)
# Standalone source copy for reproducibility.
