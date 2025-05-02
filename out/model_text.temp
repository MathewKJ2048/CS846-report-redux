open util/ordering[State] as ord // definimos el estado como un conjunto ordenado

sig TrafficLight { state : set State}
abstract sig Color {}
one sig Red, Ambar, Green extends Color {}

sig State { light: one Color }

fun colorSequence: set Color -> Color {

	(Green->Ambar)+(Red->Green)+(Ambar->Red)+(Color<:iden)
}

pred changeLight[e1, e2: State]{ e1.light -> e2.light in colorSequence}

fact traces{
	init[ord/first]
	all e: State-ord/last | let e1 = e.next | changeLight[e,e1]
}


pred init[e:State]{e.light=Red}

pred search {ord/last.light = Ambar}

pred searchAnyState { some e:State | e.light = Ambar}

run search for 100 State, 1 TrafficLight
run searchAnyState for 100 State, 1 TrafficLight
