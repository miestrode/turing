(
  define
  (problem instance-3)
  (:domain freecell)
  (:objects s3 h4 ca n0 h0 h3 h2 n4 n3 ha n8 d0 n6 s0 sa h n1 n11 d c d4 n12 n10 n7 c2 n5 s n2 s2 da n9 n13 d3 c4 d2 c0 c3 s4)
  (
    :init
    (canstack s3 h4)
    (num_______ n1)
    (canstack s3 d4)
    (suit sa s)
    (successor n1 n0)
    (on ha ca)
    (clear ha)
    (suit______ h)
    (canstack d2 c3)
    (value ha n1)
    (home s0)
    (successor n5 n4)
    (suit c0 c)
    (value da n1)
    (successor n12 n11)
    (clear c4)
    (successor n2 n1)
    (suit ha h)
    (card______ sa)
    (value sa n1)
    (value d2 n2)
    (suit d0 d)
    (home h0)
    (value d0 n0)
    (canstack ha c2)
    (bottomcol d2)
    (suit d4 d)
    (value d4 n4)
    (value s4 n4)
    (canstack h3 s4)
    (card______ d2)
    (suit c2 c)
    (canstack da c2)
    (card______ c0)
    (clear h3)
    (num_______ n12)
    (successor n7 n6)
    (successor n4 n3)
    (canstack c3 d4)
    (suit d2 d)
    (card______ d0)
    (suit s4 s)
    (clear d3)
    (value s3 n3)
    (card______ h2)
    (num_______ n5)
    (suit d3 d)
    (num_______ n13)
    (bottomcol ca)
    (suit h0 h)
    (on s3 da)
    (clear s3)
    (on sa d2)
    (value s2 n2)
    (bottomcol h2)
    (card______ ca)
    (suit______ s)
    (suit da d)
    (on da d4)
    (value ca n1)
    (num_______ n4)
    (canstack c3 h4)
    (canstack h2 c3)
    (num_______ n11)
    (on h3 s2)
    (canstack d3 s4)
    (bottomcol c3)
    (card______ c3)
    (card______ da)
    (card______ s0)
    (canstack ca h2)
    (colspace n0)
    (card______ ha)
    (canstack s2 h3)
    (value s0 n0)
    (suit c4 c)
    (clear h4)
    (num_______ n3)
    (value h2 n2)
    (card______ c4)
    (canstack d2 s3)
    (canstack s2 d3)
    (clear h2)
    (card______ s4)
    (value c3 n3)
    (suit h4 h)
    (card______ h0)
    (suit s0 s)
    (bottomcol s2)
    (card______ s2)
    (successor n9 n8)
    (value c0 n0)
    (successor n6 n5)
    (suit c3 c)
    (value c2 n2)
    (suit ca c)
    (successor n10 n9)
    (card______ h3)
    (canstack sa d2)
    (canstack h3 c4)
    (clear s4)
    (successor n3 n2)
    (num_______ n9)
    (successor n13 n12)
    (bottomcol d3)
    (card______ d3)
    (canstack d3 c4)
    (value h0 n0)
    (canstack ca d2)
    (canstack c2 h3)
    (suit h2 h)
    (num_______ n0)
    (on s4 c2)
    (num_______ n7)
    (card______ s3)
    (suit h3 h)
    (suit______ c)
    (suit______ d)
    (suit s3 s)
    (canstack c2 d3)
    (num_______ n2)
    (successor n11 n10)
    (card______ c2)
    (home c0)
    (num_______ n10)
    (num_______ n6)
    (on c2 sa)
    (num_______ n8)
    (canstack sa h2)
    (value h3 n3)
    (canstack h2 s3)
    (cellspace n4)
    (bottomcol h4)
    (card______ h4)
    (suit s2 s)
    (value d3 n3)
    (canstack ha s2)
    (on c4 c3)
    (bottomcol d4)
    (value h4 n4)
    (successor n8 n7)
    (home d0)
    (card______ d4)
    (value c4 n4)
    (canstack da s2)
    (injected--0)
  )
  (
    :goal
    (
      and
      (home c4)
      (home d4)
      (home h4)
      (home s4)
      (injected--0)
    )
  )
)