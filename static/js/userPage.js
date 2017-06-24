var getString = '/users/' + url + '/getBeers'

// Asynch get JSON of beers (I know, this is bad, but I need the object later and don't feel like being in callback hell)
var result
$.getJSON({'url': getString, 'async': false}, function(r){
    result = r
})

// Set the user's name on the page
$('#nameHeader').text('Welcome ' + result['name'])

// Build the brewery selectors
var sortedBreweries = []
for (brewery in result.beer) {
    sortedBreweries.push(brewery)
}
sortedBreweries.sort()
for (var i =0; i < sortedBreweries.length; i++) {
    $('#brewerySelector').append('<option>' + sortedBreweries[i] + '</option>')
}
 
$('#brewerySelector').append('<option>Other</option>')

// Build beer list based on currently selected brewery
buildBeerSelector($('#brewerySelector').val())

// Add change listeners to the brewery objects so that the beer list is rebuilt when the brewery changes.
$('#brewerySelector').on('change', function(){
    buildBeerSelector($(this).val())
})

// Add change listener to beer object so that we can display existing rating, if applicable
$('#beerSelector').on('change', function() {
    displayBeerRating($('#brewerySelector').val(), $(this).val())
})

$('#submitChanges').on('click', editRating)

// Emptys the list of beers and refreshes based on the brewery selected
function buildBeerSelector(brewery) {
    // Build out brewery if other
    if(brewery === 'Other'){
        $('#otherBrewery').val('')
        $('#otherBrewery').css('display', 'block')
        $('#beerSelector').empty()
        $('#beerSelector').append('<option>Other</option>')
        $('#otherBeer').css('display', 'block')
        displayBeerRating('Other', 'Other')
        return
    } else {
        $('#otherBrewery').css('display', 'none')
        $('#otherBeer').css('display', 'none')
    }

    $('#beerSelector').empty()
    var sortedBeers = []
    for (beer in result.beer[brewery]){
        sortedBeers.push(beer)
    }
    sortedBeers.sort()
    for (var i = 0; i < sortedBeers.length; i++){
        $('#beerSelector').append('<option>' + sortedBeers[i] + '</option>')
    }
    $('#beerSelector').append('<option>Other</option>')
    // Display rating or tasting notes
    displayBeerRating($('#brewerySelector').val(), $('#beerSelector').val())

}

function editRating(){
    var postStr = '/users/' + url + '/editRating'

    // If brewery is other, then we need to get the name of the new brewery
    if ($('#brewerySelector').val() === 'Other') {
        var brewery = $('#otherBrewery').val()
        $('#brewerySelector').append('<option>' + brewery + '</option>')
    } else{
        var brewery = $('#brewerySelector').val()
    }

    // If beer is other, then we need to get the name of the new beer and update the beer list
    if ($('#beerSelector').val() === 'Other') {
        var beer = $('#otherBeer').val()
        $('#beerSelector').append('<option>' + beer + '</option>')
        } else {
        var beer = $('#beerSelector').val()
    }

    // Set if beer is a must try
    var mustTry = $('[name="mustTry"]').prop('checked')

    var rating = $('#rating').val()
    var tastingNotes = $('#tastingNotes').val()
    var data = {
        'brewery': brewery,
        'beer': beer,
        'mustTry': mustTry,
        'rating': rating,
        'tastingNotes': tastingNotes
    }

    // Update original response that we got (add if this was a different beer)
    if ($('#brewerySelector').val() === 'Other') {
        result.beer[brewery] = {}
    }
    if ($('#beerSelector').val() === 'Other') {
        result.beer[brewery][beer] = {}
    }
    result.beer[brewery][beer]['rating'] = rating
    result.beer[brewery][beer]['notes'] = tastingNotes
    $.post(postStr, data, function(r) {
        if(r === 'success') {
            $('.alert').text('Successfully updated ' + brewery + ' ' + beer)
            $('.alert').removeClass('alert-danger').addClass('alert-success')
            $('.alert').css('display', 'block')
        }
    })
    .fail(function() {
        $('.alert').text('Uh oh! Something went wrong. Please refresh and try again.')
        $('.alert').removeClass('alert-success').addClass('alert-danger')
        $('.alert').css('display', 'block')
    })
}

function displayBeerRating (brewery, beer) {
    // Account for other beer
    $('.alert').css('display', 'none')
    if (beer === 'Other') {
        $('#otherBeer').val('')
        $('#otherBeer').css('display', 'block')
        $('#rating').val(1)
        $('#tastingNotes').val('')
        return
    }
    $('#otherBeer').css('display', 'none')
    // Default to rating of null
    if(result.beer[brewery][beer]['rating'] !== ''){
        $('#rating').val(result.beer[brewery][beer]['rating'])
    } else {
        $('#rating').val('')
    }
    
    $('#tastingNotes').val(result.beer[brewery][beer]['notes'])
}
