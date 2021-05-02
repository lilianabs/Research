
## Implementation of a deterministic finite automaton in Mathematica 


rule = {{1, 0} -> 2, {1, 1} -> 1, {2, 0} -> 1, {2, 1} -> 2};

automatonStep[rule_, state_, 
  s_] := {rule, {state, ToExpression[StringPart[s, 1]]} /. rule, 
  StringDrop[s, 1]}

automatonStep[rule, 1, "010"]

{{{1, 0} -> 2, {1, 1} -> 1, {2, 0} -> 1, {2, 1} -> 2}, 2, "10"}

automatonCompute[rule_, initState_, s_, finalStates_] := 
 acceptWordAutomaton[
  NestWhileList[
   automatonStep[#[[1]], #[[2]], #[[3]]] &, {rule, initState, s}, 
   ToString[#[[3]]] != "" &], finalStates]

automatonCompute[rule, 1, "010", {1}]

acceptWordAutomaton[result_, finalStates_List] := 
 MemberQ[finalStates, result[[Length[result], 2]]]

