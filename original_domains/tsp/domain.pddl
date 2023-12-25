(define (domain tsp)
  (:predicates
     (at ?x)
     (visited ?x))

  (:action move
	:parameters (?x ?y)
	:precondition (at ?x)
	:effect (and (not (at ?x)) (at ?y) (visited ?y))))
