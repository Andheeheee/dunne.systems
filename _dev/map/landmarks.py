# Builds the map's SVG overlay: fiber path, landmarks, labels. Map units 1600x1000.
import math
SH='<ellipse class="sh" cx="10" cy="3" rx="{rx}" ry="{ry}" fill="#000" opacity=".32"/>'
def leds(x0,y0,cols,rows,dx,dy,cls="led"):
    return "".join(f'<rect class="{cls}" x="{x0+c*dx}" y="{y0+r*dy}" width="3" height="3" style="animation-delay:{((c*7+r*3)%10)/10:.1f}s"/>' for r in range(rows) for c in range(cols))
ART={
"needle":SH.format(rx=34,ry=9)+'''
<path d="M-10 -78 L-26 0 H-18 L-4 -60 L0 -66 L4 -60 L18 0 H26 L10 -78 Z" fill="#dfe4ea" stroke="#5d6672" stroke-width="1.5"/>
<path d="M4 -60 L18 0 H26 L10 -78 Z" fill="#b6bec9"/>
<rect x="-13" y="-62" width="26" height="4" fill="#c9cfd8" stroke="#5d6672"/>
<rect x="-3" y="-130" width="6" height="60" fill="#c9cfd8" stroke="#5d6672" stroke-width="1"/>
<path d="M-40 -136 Q0 -152 40 -136 L32 -126 Q0 -118 -32 -126 Z" fill="#f4f6f9" stroke="#4d5662" stroke-width="1.5"/>
<path d="M-32 -126 Q0 -118 32 -126 L28 -121 Q0 -114 -28 -121 Z" fill="#9aa6b6"/>
<g fill="#ffd25a">'''+"".join(f'<rect x="{x}" y="-133" width="4" height="3"/>' for x in range(-30,30,8))+'''</g>
<path d="M-14 -146 Q0 -152 14 -146 L10 -141 H-10 Z" fill="#e8743a" stroke="#4d5662"/>
<rect x="-1.2" y="-176" width="2.4" height="30" fill="#8a94a3"/><circle class="beacon" cx="0" cy="-177" r="2.6" fill="#ff4a3a"/>''',
"akamai":SH.format(rx=58,ry=13)+'''
<path d="M-56 -8 L0 14 L56 -8 L56 -46 L0 -24 L-56 -46 Z" fill="#8f9aa8"/>
<path d="M0 14 L56 -8 L56 -46 L0 -24 Z" fill="#6c7786"/>
<path d="M-56 -46 L0 -68 L56 -46 L0 -24 Z" fill="#c9d1db" stroke="#4d5662" stroke-width="1"/>
<path d="M-56 -8 L0 14 L56 -8 L56 -46 L0 -24 L-56 -46 Z" fill="none" stroke="#3d4652" stroke-width="1.5"/>
<g><path d="M-26 -52 L-12 -46 L2 -52 L-12 -58 Z" fill="#e6ebf1" stroke="#4d5662"/><path d="M-26 -52 V-58 L-12 -64 L2 -58 V-52" fill="none" stroke="#4d5662"/><circle cx="-12" cy="-58" r="4" fill="#9aa6b6" stroke="#4d5662"/>
<path d="M14 -44 L26 -39 L38 -44 L26 -49 Z" fill="#e6ebf1" stroke="#4d5662"/><circle cx="26" cy="-47" r="3.5" fill="#9aa6b6" stroke="#4d5662"/></g>
<path d="M-50 -22 L-6 -5" stroke="#e8743a" stroke-width="4"/>
<g transform="matrix(1 .39 0 1 -50 -40)">'''+leds(0,0,11,3,4,6)+'''</g>
<g transform="matrix(1 -.39 0 1 6 -14)">'''+leds(0,0,11,3,4,6,"led led2")+'''</g>
<rect x="40" y="-86" width="2" height="34" fill="#4d5662"/><circle class="beacon" cx="41" cy="-87" r="2.4" fill="#ff4a3a"/>''',
"homelab":SH.format(rx=50,ry=12)+'''
<path d="M-44 0 V-40 L-20 -62 L4 -40 V0 Z" fill="#efe3c8" stroke="#5a4a30" stroke-width="1.5"/>
<path d="M-48 -38 L-20 -66 L8 -38" fill="none" stroke="#8e2f22" stroke-width="7" stroke-linejoin="round"/>
<rect x="-30" y="-30" width="9" height="9" fill="#9fd3ff" stroke="#5a4a30"/><rect x="-14" y="-30" width="9" height="9" fill="#9fd3ff" stroke="#5a4a30"/>
<rect x="-26" y="-16" width="11" height="16" fill="#6b4a2a"/>
<path d="M4 0 V-34 L46 -34 V0 Z" fill="#e3d6b8" stroke="#5a4a30" stroke-width="1.5"/><path d="M0 -34 L50 -34 L46 -42 L4 -42 Z" fill="#8e2f22"/>
<rect x="10" y="-28" width="30" height="28" fill="#1a1f25"/><rect x="10" y="-28" width="30" height="5" fill="#b9b2a0" stroke="#5a4a30"/>
<rect x="15" y="-22" width="20" height="22" fill="#2b333b" stroke="#0d1014"/>'''+leds(18,-19,4,5,4,4)+'''
<rect x="-12" y="-76" width="7" height="16" fill="#7a3a2a"/>
<g class="smoke" fill="#e9eef3"><circle cx="-8" cy="-82" r="5"/><circle cx="-4" cy="-92" r="6"/><circle cx="2" cy="-103" r="7"/></g>''',
"grc":SH.format(rx=62,ry=13)+'''
<rect x="-58" y="-40" width="116" height="40" fill="#b5523a" stroke="#4a2218" stroke-width="1.5"/>
<g fill="#f4efe4" stroke="#7a6a58">'''+"".join(f'<rect x="{x}" y="-38" width="6" height="38"/>' for x in (-20,-8,4,16))+'''</g>
<path d="M-28 -40 L0 -58 L28 -40 Z" fill="#f4efe4" stroke="#7a6a58" stroke-width="1.5"/>
<g fill="#ffe79a" stroke="#4a2218">'''+"".join(f'<rect x="{x}" y="-30" width="8" height="10"/><rect x="{x}" y="-15" width="8" height="10"/>' for x in (-52,-40,32,44))+'''</g>
<rect x="-8" y="-86" width="16" height="30" fill="#c86a4e" stroke="#4a2218"/><path d="M-11 -86 L0 -98 L11 -86 Z" fill="#2e5d8a" stroke="#1a2a3a"/>
<circle cx="0" cy="-74" r="5.5" fill="#fff" stroke="#4a2218"/><path d="M0 -74 V-77.5 M0 -74 H2.5" stroke="#1a1a1a" stroke-width="1"/>
<rect x="-40" y="6" width="80" height="14" rx="2" fill="#1b3f8a" stroke="#0b1a3a"/><text x="0" y="16.5" font-size="9" font-weight="bold" fill="#ffe23a" text-anchor="middle" font-family="Tahoma,sans-serif">PC REPAIR SHOP</text>''',
"school":SH.format(rx=60,ry=12)+'''
<rect x="-56" y="-30" width="96" height="30" fill="#d9b36a" stroke="#5a4520" stroke-width="1.5"/><rect x="-60" y="-34" width="104" height="5" fill="#8a6a3a"/>
<g fill="#cfe8ff" stroke="#5a4520">'''+"".join(f'<rect x="{x}" y="-24" width="9" height="9"/>' for x in (-48,-34,-20,-6,8,22))+'''</g>
<rect x="-8" y="-12" width="14" height="12" fill="#6b4a2a"/>
<rect x="-50" y="-70" width="2" height="40" fill="#6d737b"/><path d="M-48 -70 H-28 V-58 H-48 Z" fill="#2e5d8a"/><path d="M-48 -64 H-28" stroke="#fff" stroke-width="2"/>
<g transform="translate(46 0)"><rect x="0" y="-8" width="26" height="8" fill="#2b5fa8" stroke="#0e2448"/><rect x="2" y="-16" width="24" height="8" fill="#3a74c4" stroke="#0e2448"/><rect x="-1" y="-24" width="25" height="8" fill="#2b5fa8" stroke="#0e2448"/>'''+leds(3,-6,5,1,4,0)+leds(5,-14,5,1,4,0)+leds(2,-22,5,1,4,0)+'''</g>''',
"pisces":SH.format(rx=60,ry=12)+'''
<rect x="-50" y="-34" width="80" height="34" fill="#dfe2e6" stroke="#4d5662" stroke-width="1.5"/>
<path d="M-24 -34 Q-10 -62 4 -34 Z" fill="#c9a24a" stroke="#6a5420" stroke-width="1.5"/><rect x="-11" y="-68" width="2" height="10" fill="#6a5420"/>
<g fill="#f4f6f9" stroke="#8a94a3">'''+"".join(f'<rect x="{x}" y="-30" width="5" height="30"/>' for x in (-44,-34,-24,-14,-4,6,16,24))+'''</g>
<path d="M-56 -34 H36 L30 -40 H-50 Z" fill="#b6bec9" stroke="#4d5662"/>
<g transform="translate(46 0)"><path d="M0 0 L8 -26 L16 0 M8 -26 V0" stroke="#4d5662" stroke-width="2" fill="none"/>
<g class="radar"><path d="M-8 -40 Q8 -20 26 -36 Q12 -52 -8 -40 Z" fill="#eef1f5" stroke="#4d5662" stroke-width="1.5"/><path d="M9 -38 L18 -48" stroke="#4d5662" stroke-width="1.5"/><circle cx="18" cy="-48" r="2" fill="#e8743a"/></g></g>''',
"ccdc":SH.format(rx=56,ry=13)+'''
<rect x="-40" y="-40" width="80" height="40" fill="#9aa1aa" stroke="#3d4450" stroke-width="1.5"/>
<g fill="#9aa1aa" stroke="#3d4450" stroke-width="1.5">'''+"".join(f'<rect x="{x}" y="-48" width="8" height="8"/>' for x in (-40,-24,-8,8,24))+'''</g>
<rect x="-56" y="-62" width="22" height="62" fill="#868d97" stroke="#3d4450" stroke-width="1.5"/><rect x="34" y="-62" width="22" height="62" fill="#868d97" stroke="#3d4450" stroke-width="1.5"/>
<g fill="#868d97" stroke="#3d4450">'''+"".join(f'<rect x="{x}" y="-70" width="6" height="8"/>' for x in (-56,-48,-40,34,42,50))+'''</g>
<path d="M-12 0 V-20 Q0 -32 12 -20 V0 Z" fill="#3a2a1a" stroke="#1a120a"/>
<rect x="-46" y="-48" width="4" height="10" fill="#1a1f25"/><rect x="44" y="-48" width="4" height="10" fill="#1a1f25"/>
<rect x="-1" y="-86" width="2" height="38" fill="#3d4450"/><path class="flag" d="M1 -86 Q12 -90 22 -84 Q12 -78 1 -80 Z" fill="#d23a2e"/>
<g transform="translate(0 -24)"><path d="M-9 -12 H9 V0 Q9 9 0 13 Q-9 9 -9 0 Z" fill="#2e5d8a" stroke="#ffe23a" stroke-width="1.5"/><path d="M-4 0 L-1 4 L5 -4" stroke="#ffe23a" stroke-width="2" fill="none"/></g>''',
"rainier":'''<circle r="90" fill="transparent"/><g transform="translate(0 -6)"><rect x="-1" y="-40" width="2.5" height="40" fill="#5a4a30"/><path class="flag" d="M1.5 -40 L22 -33 L1.5 -26 Z" fill="#ffe23a" stroke="#5a4a30"/></g>''',
}
LM=[ # key, x, y, label lines, hit box (w,h,dy)
 ("needle",760,290,["Space Needle","(Contact)"],(110,210,-170)),
 ("akamai",858,505,["Akamai","Data Center"],(140,120,-90)),
 ("homelab",1015,615,["Home Lab","(Renton)"],(120,130,-110)),
 ("school",835,735,["High School","Labs"],(160,100,-75)),
 ("grc",1085,835,["Green River","College"],(140,130,-100)),
 ("pisces",470,905,["PISCES SOC"],(150,100,-75)),
 ("ccdc",235,330,["PRCCDC","Arena"],(130,120,-90)),
 ("rainier",1450,840,["Mt. Rainier","(About me)"],(160,160,-100)),
]
def lab(lines,y0):
    t=f'<text class="lbl" y="{y0}">'+"".join(f'<tspan x="0" dy="{0 if i==0 else 21}">{l}</tspan>' for i,l in enumerate(lines))+'</text>'
    return t
# fiber path through landmarks (Catmull-Rom → cubic Béziers)
def cr(pts):
    d=f"M{pts[0][0]} {pts[0][1]}"
    for i in range(len(pts)-1):
        p0=pts[i-1] if i>0 else pts[i];p1=pts[i];p2=pts[i+1];p3=pts[i+2] if i+2<len(pts) else p2
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6);c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        d+=f" C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]} {p2[1]}"
    return d
main=cr([(240,348),(420,250),(600,318),(760,302),(790,410),(858,516),(950,560),(1015,628),(930,690),(835,748),(960,810),(1085,848),(1250,830),(1390,808)])
branch=cr([(858,516),(720,590),(610,720),(540,820),(470,915)])
F=''.join(f'''<path d="{d}" class="f0"/><path d="{d}" class="f1"/><path d="{d}" class="f2"/><path d="{d}" class="f3"/>''' for d in (main,branch))
ferry='<path id="ferryroute" d="M430 300 C520 270 620 330 712 318" fill="none"/><g class="ferry"><path d="M-30 0 Q0 7 30 0 L26 -7 H-26 Z" fill="#f4f6f9" stroke="#2b3440" stroke-width="1.2"/><rect x="-16" y="-14" width="30" height="7" fill="#fff" stroke="#2b3440" stroke-width="1"/><rect x="-6" y="-21" width="12" height="7" fill="#e9eef3" stroke="#2b3440" stroke-width="1"/><path d="M-14 -11 H12" stroke="#2e7d4a" stroke-width="2"/><rect x="2" y="-27" width="3" height="6" fill="#2b3440"/><path d="M-30 3 Q-46 6 -62 2" stroke="#d8f2ff" stroke-width="2.5" fill="none" opacity=".8"/><animateMotion dur="38s" repeatCount="indefinite" rotate="0" keyPoints="0;1;1;0;0" keyTimes="0;.42;.5;.92;1" calcMode="linear"><mpath href="#ferryroute"/></animateMotion></g>'
out=[f'<svg class="map-svg" viewBox="0 0 1600 1000" width="1600" height="1000" aria-hidden="false">{ferry}<g class="fiber">{F}</g>']
for k,x,y,lines,(hw,hh,hy) in LM:
    out.append(f'<g class="lm" data-k="{k}" transform="translate({x} {y}) scale(1.3)" tabindex="0" role="button" aria-label="{" ".join(lines)}">'
               f'<rect class="hit" x="{-hw/2}" y="{hy}" width="{hw}" height="{hh+46}" fill="transparent"/>'
               f'<ellipse class="ring" cx="0" cy="2" rx="62" ry="16"/><g class="art">{ART[k]}</g>{lab(lines,34 if k!="rainier" else -60)}</g>')
out.append('</svg>')
open(__import__('pathlib').Path(__file__).with_name('overlay.svg'),'w').write("".join(out))
print(len("".join(out))//1024,'KB')
