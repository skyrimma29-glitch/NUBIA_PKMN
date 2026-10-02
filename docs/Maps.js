const W=20, H=14, borde='^', suelo=',';
copy(Array.from({length:H},(_,y)=>"'"+Array.from({length:W},(_,x)=>
  (x<1||y<1||x>=W-1||y>=H-1)?borde:suelo).join('')+"'").join(','))