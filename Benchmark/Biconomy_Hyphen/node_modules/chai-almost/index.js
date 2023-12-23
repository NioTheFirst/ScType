'use strict'

var deepEqual = require('deep-eql')
var type = require('type-detect')

var DEFAULT_TOLERANCE = 1e-6

/**
 * small utility functions
 */
function isNumber (val) {
  return type(val) === 'number'
}

function bothNumbers (left, right) {
  return isNumber(right) && isNumber(left)
}

function almostEqual (left, right, tol) {
  return Math.abs(left - right) <= tol
}

/**
 * Makes a comparator function to be passed to deepEqual.
 * The returned function will return null if both arguments are not numbers,
 * indicating that deepEqual should proceed with other equality checks
 */
function comparator (tolerance) {
  return function (left, right) {
    if (bothNumbers(left, right)) {
      return almostEqual(left, right, tolerance)
    }
    return null
  }
}

/**
 * Sets global tolerance and returns a function to be passed to chai.use
 * @see http://chaijs.com/guide/plugins/
 */
function chaiAlmost (customTolerance) {
  var standardTolerance = customTolerance || DEFAULT_TOLERANCE

  return function (chai, utils) {
    var Assertion = chai.Assertion
    var flag = utils.flag

    /**
     * Returns a new shallow equality function to override
     * .equal, .equals, .eq that tests 'almost' equality
     * if both values are numbers and a 'tolerance' flag is set.
     * Sends to deep equality check if deep flag is set
     */
    function overrideAssertEqual (_super) {
      return function assertEqual (val, msg) {
        if (msg) flag(this, 'message', msg)

        var deep = flag(this, 'deep')
        var tolerance = flag(this, 'tolerance')

        if (deep) {
          return this.eql(val)
        } else if (tolerance && bothNumbers(val, this._obj)) {
          this.assert(almostEqual(val, this._obj, tolerance),
            'expected #{this} to almost equal #{exp}',
            'expected #{this} to not almost equal #{exp}',
            val,
            this._obj,
            true
          )
        } else {
          return _super.apply(this, arguments)
        }
      }
    }

    /**
     * Returns a new deep equality function to override
     * .eql, .eqls that tests 'almost' equality if both corresponding
     * values are numbers and tolerance flag is set
     */
    function overrideAssertEql (_super) {
      return function assertEql (val, msg) {
        if (msg) flag(this, 'message', msg)

        var tolerance = flag(this, 'tolerance')

        if (tolerance) {
          this.assert(
            deepEqual(val, this._obj, { comparator: comparator(tolerance) }),
            'expected #{this} to deeply almost equal #{exp}',
            'expected #{this} to not deeply almost equal #{exp}',
            val,
            this._obj,
            true
          )
        } else {
          return _super.apply(this, arguments)
        }
      }
    }

    /**
     * .almost() method. To be used at the end of the chain like:
     * expect(4).to.not.be.almost(5, 1.5). Simply adds tolerance flag then calls
     * .equal. This will redirect to .eql if deep flag set
     */
    function method (val, toleranceOverride) {
      var tolerance = toleranceOverride || standardTolerance

      flag(this, 'tolerance', tolerance)

      return this.equal(val)
    }

    /**
     * .almost chainable property to be used like:
     * expect(3.99999999).to.almost.equal(4). Simply adds
     * tolerance flag to be read by equality checking methods
     */
    function chainingBehavior () {
      flag(this, 'tolerance', standardTolerance)
    }

    Assertion.addChainableMethod('almost', method, chainingBehavior)

    Assertion.overwriteMethod('equal', overrideAssertEqual)
    Assertion.overwriteMethod('equals', overrideAssertEqual)
    Assertion.overwriteMethod('eq', overrideAssertEqual)

    Assertion.overwriteMethod('eql', overrideAssertEql)
    Assertion.overwriteMethod('eqls', overrideAssertEql)
  }
}

module.exports = chaiAlmost
