var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0;i<updateBtns.length;i++){
  updateBtns[i].addEventListener('click',function(){
    var productId = this.dataset.product
    var action = this.dataset.action
    console.log('productId:',productId,'action:',action)
    updateUserOrder(productId)
  })
}

function updateUserOrder(productId){
  var url = '/login/'
  fetch(url,{
    method:'POST',
    headers:{
      'Content-Type':'application/json'
    },
    body:JSON.stringify({'productId':productId})
  })

  .then((response)=>{
    return resonse.json()
  })
}
