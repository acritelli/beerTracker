var getString
var result
var addOtherBrewery = true
var addOtherBeer = true

// Builds a page based on desired action (passed in template) with the specified brewery/beer selected
function buildPage (action, selectedBrewery, selectedBeer) {
    // Decode brewery and beer selectors, in case there were any HTML special chars
    selectedBrewery = $("<textarea/>").html(selectedBrewery).text();
    selectedBeer = $("<textarea/>").html(selectedBeer).text();

    // Set the appropriate AJAX string based on action
    if (action === 'displayAll') {
        getString = '/users/' + url + '/getBeers'
    } else if (action === 'displayMustTry') {
        addOtherBrewery = false
        addOtherBeer = false
        getString = '/users/' + url + '/getMustTryBeers'
    }
    // Get JSON and build the page. Return to home if error
    $.ajax({'url': getString,
        'dataType': 'json',
        'success': function(r) {
            result = r
            renderFullBeerList(selectedBrewery, selectedBeer)
        },
        'error': function() {
            window.location='/'
        }
    })
}

// Builds lists with all beers (as opposed to just must trys)
function renderFullBeerList (selectedBrewery, selectedBeer) {
    $('#nameHeader').text('Welcome ' + result['name'])
    buildBrewerySelector(selectedBrewery, selectedBeer)
}

function buildBrewerySelector (selectedBrewery, selectedBeer) {
    // Build the brewery selectors
    $('#brewerySelector').empty()
    var sortedBreweries = []
    for (brewery in result.beer) {
        sortedBreweries.push(brewery)
    }
    sortedBreweries.sort()
    for (var i =0; i < sortedBreweries.length; i++) {
        $('#brewerySelector').append('<option>' + sortedBreweries[i] + '</option>')
    }
    if (addOtherBrewery) {
        $('#brewerySelector').append('<option>Other</option>')
    }

    if (selectedBrewery) {
        $('#brewerySelector').val(selectedBrewery)
    }

    // Build beer list based on currently selected brewery
    buildBeerSelector($('#brewerySelector').val(), selectedBeer)
}

function refreshListeners () {
    // Add change listeners to the brewery objects so that the beer list is rebuilt when the brewery changes.
    $('#brewerySelector').on('change', function(){
        buildBeerSelector($(this).val())
    })

    // Add change listener to beer object so that we can display existing rating, if applicable
    $('#beerSelector').on('change', function() {
        displayBeerRating($('#brewerySelector').val(), $(this).val())
    })
}

// Emptys the list of beers and refreshes based on the brewery selected
function buildBeerSelector(brewery, selectedBeer) {
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

    if (addOtherBeer) {
        $('#beerSelector').append('<option>Other</option>')
    }

    if (selectedBeer) {
        $('#beerSelector').val(selectedBeer)
    }

    // Display rating or tasting notes
    displayBeerRating($('#brewerySelector').val(), $('#beerSelector').val())

    refreshListeners()
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

    // Toggle mustTry
    if(result.beer[brewery][beer]['mustTry']) {
        $('#mustTry').bootstrapToggle('on')
    } else {
        $('#mustTry').bootstrapToggle('off')
    }
    
    $('#tastingNotes').val(result.beer[brewery][beer]['notes'])
}
