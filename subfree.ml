(* This file contains the subfree function, which is the key result *)

(* We need a data structure to represent rooted trees with coloured half-edges *)
(* The main building block is that of a node, which can half child nodes and child half-edges *)
(* The child nodes will be kept in a list, the half-edges in a multiset *)

(* general code *)
(* generic fold left implementation *)
let rec fold f a l =
    match l with
    | [] -> a
    | h :: t -> fold f (f a h) t

(* computes cross product of entries in l, a list of lists *)
let rec product'' l = 
    (* We need to do the cross product of our current list and all the others
     * so we define a helper function for that *)
    let rec aux ~acc l1 l2 = match l1, l2 with
    | [], _ | _, [] -> acc
    | h1::t1, h2::t2 -> 
        let acc = (h1::h2)::acc in
        let acc = (aux ~acc t1 l2) in
        aux ~acc [h1] t2
    (* now we can do the actual computation *)
    in match l with
    | [] -> []
    | [l1] -> List.map (fun x -> [x]) l1
    | l1::tl ->
        let tail_product = product'' tl in
        aux ~acc:[] l1 tail_product

(* fact x computes x!. Linear time in x. *)
let rec fact x =
    if x <= 1 then 1 else x * fact (x - 1)

(* multisets *)                                                                  
(* multiset is a list of elements with their multiplicities *)
type 'a mset = ('a * int) list

(* mult gets the multiplicity of element e in multiset xs *)
(* O(n) runtime where n is the number of distinct elements in the multiset *)
let rec mult (xs : 'a mset) (e : 'a) : int =
    match xs with
    | [] -> 0
    | (el, ct)::t -> if el = e then ct else (mult t e)

(* sum produces the union of xs and ys *)
(* We go through the list (linear), and at each step perform a linear amount of work, 
   thus runtime is O((m+n)*max(m,n)) where m is length of xs, n is length of ys, ie basically n^2 *)
(* This could be improved by sorting both multisets first *)
let rec sum (xs : 'a mset) (ys : 'a mset) : ('a mset) =
    (* we look at each element of xs concatenated to ys. If the element is already in the accumulated list, we return it.
       Otherwise, append the item with its count in xs and ys to the accumulator.  *)
    fold (fun acc (k, _) ->
    if (mult acc k) <> 0 then acc
    else (k, (mult xs k) + (mult ys k))::acc)
    [] (xs @ ys)

(* converts a list of elements to a multiset *)
(* basically n^3 time, this could be done way faster by improving sum *)
let lst_to_mset lst =
    List.fold_left (fun acc h -> sum acc [(h,1)]) [] lst


(* trees *)
(* tree is a list of multiset half-edges, and a list of child trees *)
(* why not use a multiset of half-edges, and a list of child trees? It seems like each half-edge's colour is represented by an entire multiset... *)
type 'a mult_tree = T of (('a mset) list) * ('a mult_tree list)

(* leaves returns a list of the leaf-labels of a tree t *)
(* visits every node of the tree once, but does a bunch of concatenation *)
let leaves t =
    (* list_aux creates a list of the leaves in a list of trees *)
    let rec list_aux lst =
        match lst with
        | [] -> []
        | h :: tl -> aux h @ list_aux tl
    and aux t =
        match t with
        | T(leaves, children) ->
            leaves @ list_aux children
    in aux t


(* stuff specific to counting subdivergence-free gluings *)

(* count_gluings counts total gluings between two trees whose leaf-labels are mset *)
(* there is some hairiness with the empty mset. Really there should be no gluings. *)
(* linear time in the total cardinality of the mset *)
let rec count_gluings mset =
    let rec count_gluings_helper ms =
        match ms with
        | [] -> 1
        | (_,i)::t -> (fact i) * (count_gluings_helper t)
    in match mset with
    | [] -> 0
    | _ -> (count_gluings_helper mset)


(* might not even need helper function *)
let rec reconstruct node lst =
    match node with
    | T(leaves,children) ->
        match lst with
        | [] -> []
        | h::tl -> T(leaves, h @ children) :: (reconstruct node tl)
        (*List.fold_left (fun acc lol -> ((T(leaves, lol @ children)) :: acc)) [] lst*)
(*let rec collect_leaves*)

let rec sublists lst =
    match lst with
    | [] -> [([],[])]
    | h::tl -> 
        let tl_sublists = (sublists tl)
        in List.map (fun (a,b) -> (h::a,b)) tl_sublists 
        @ List.map (fun (a,b) -> (a,h::b)) tl_sublists

let rec combine node child_results =
    match node with
    | T(leaves,children) ->
        match child_results with
        | [] -> T(leaves,children)
        | T(newleaves,newchildren) :: tl ->
            combine (T(leaves @ newleaves, newchildren @ children )) tl

(* could easily combine reconstruct and group reconstruct *)
let rec group_reconstruct node lol =
    (* need to remove the first node from each entry in lol *)
    match node with
    | T(leaves,children) ->
        match lol with
        | [] -> []
        | h :: tl -> (combine (T(leaves,children)) h) :: (group_reconstruct node tl)

let rec union_leaves t =
    (* acc is a multiset of leaves so far *)
    let rec list_aux lst =
        match lst with
        | [] -> []
        | h :: tl -> sum (aux h) (list_aux tl)
    and aux t =
        match t with
        | T(leaves, children) ->
            sum (List.fold_left sum [] leaves) (list_aux children)
    in aux t

(* major problem... missing a lot of cases where the cut is the first edge *)
(* really need that inside the cartesian product *)
let rec partition t =
    match t with
    (* if t has no children, there's nowhere to cut *)
    | T(_,[]) -> []
    | T([],[child]) -> 
        T([(union_leaves child)],[]) :: (reconstruct (T([],[])) (product'' [(partition child)])) 
    | T(leaves, children) ->
        let kidsubsets = List.filter (fun (a,_) -> a <> []) (sublists children)
        in List.fold_left (fun acc (chosen,ignored) ->
            group_reconstruct (T(leaves, ignored)) 
            (product'' (List.map partition (List.map (fun x -> (T([],[x]))) chosen)))
            @ acc)
        [] kidsubsets
(*
let f1 = T([[('a',1)];[('a',1)]],[]);;
let f2 = T([],[f1;f1]);;
let f3 = T([],[f2;f2]);;
let f4 = T([],[f3;f3]);;
let f5 = T([],[f4;f4]);;

print_int (List.length (partition f5));;
*)

let compare_mset (v1, n1) (v2, n2) =
    if v1 = v2 && n1 = n2 then 0
    else if v1 = v2 && n1 > n2 then 1
    else if v1 = v2 && n1 < n2 then -1
    else if v1 > v2 then 1
    else if v1 < v2 then -1
    else 0 (* shouldn't happen *)

let rec contains_all ms1 ms2 =
    List.fold_left (fun acc h -> (List.mem h ms2) && acc) true ms1

let equal ms1 ms2 =
    contains_all ms1 ms2 && contains_all ms2 ms1

let rec leaf_fact leaves =
    match leaves with
    | [] -> 1
    | h::t ->
        (List.fold_left (fun acc (_,i) -> (fact i)*acc) 1 h) * (leaf_fact t)

let rec build_assoc leaves =
    let rec aux leaves acc label =
        match leaves with
        | [] -> acc
        | h :: t ->
            if List.mem_assoc h acc then aux t acc label
            else aux t ((h,[(label,1)])::acc) (label+1)
    in aux leaves [] 1

let rec relabel leaves assoc =
    match leaves with
    | [] -> []
    | h :: tl -> List.assoc h assoc :: (relabel tl assoc)

let rec relabel_tree t assoc =
    let rec aux_list lst =
        match lst with
        | [] -> []
        | h :: tl -> (aux h) :: aux_list tl
    and aux t =
        match t with
        | T(leaves, children) -> T(relabel leaves assoc, aux_list children)
    in aux t

let rec subfree t1 t2 =
    let leaf_mset = lst_to_mset (leaves t1)
    in (count_gluings leaf_mset) - (pair (partition t1) (partition t2)) 
and pair l1 l2 =
    match l1, l2 with
    | [], _ | _, [] -> 0
    | h1::t1, h2::t2 ->
        let h1_leaves = leaves h1 in
        let head_contrib = 
            if (equal (lst_to_mset h1_leaves) (lst_to_mset (leaves h2))) 
            then let assoc_list = build_assoc h1_leaves in
            (leaf_fact h1_leaves) * 
            (subfree (relabel_tree h1 assoc_list) (relabel_tree h2 assoc_list)) else 0
        in head_contrib + (pair [h1] t2) + (pair t1 l2)

let leaf = [(1,1)];;
let basic = T([leaf],[]);;
let b2 = T([leaf],[basic]);;
let b3 = T([leaf], [b2]);;
let d1 = T([],[b2;b2]);;
let d2 = T([], [b3;b3]);;
