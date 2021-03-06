# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""The Gaussian distribution: conjugate posterior closed form calculations.

@@known_sigma_posterior
@@known_sigma_predictive
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.contrib.distributions.python.ops.gaussian import Gaussian  # pylint: disable=line-too-long

from tensorflow.python.ops import math_ops


def known_sigma_posterior(prior, sigma, s, n):
  """Posterior Gaussian distribution with conjugate prior on the mean.

  This model assumes that `n` observations (with sum `s`) come from a
  Gaussian with unknown mean `mu` (described by the Gaussian `prior`)
  and known variance `sigma^2`.  The "known sigma posterior" is
  the distribution of the unknown `mu`.

  Accepts a prior Gaussian distribution object, having parameters
  `mu0` and `sigma0`, as well as known `sigma` values of the predictive
  distribution(s) (also assumed Gaussian),
  and statistical estimates `s` (the sum(s) of the observations) and
  `n` (the number(s) of observations).

  Returns a posterior (also Gaussian) distribution object, with parameters
  `(mu', sigma'^2)`, where:

  ```
  mu ~ N(mu', sigma'^2)
  sigma'^2 = 1/(1/sigma0^2 + n/sigma^2),
  mu' = (mu0/sigma0^2 + s/sigma^2) * sigma'^2.
  ```

  Distribution parameters from `prior`, as well as `sigma`, `s`, and `n`.
  will broadcast in the case of multidimensional sets of parameters.

  Args:
    prior: `Gaussian` object of type `dtype`:
      the prior distribution having parameters `(mu0, sigma0)`.
    sigma: tensor of type `dtype`, taking values `sigma > 0`.
      The known stddev parameter(s).
    s: Tensor of type `dtype`.  The sum(s) of observations.
    n: Tensor of type `int`.  The number(s) of observations.

  Returns:
    A new Gaussian posterior distribution object for the unknown observation
    mean `mu`.

  Raises:
    TypeError: if dtype of `s` does not match `dtype`, or `prior` is not a
      Gaussian object.
  """
  if not isinstance(prior, Gaussian):
    raise TypeError("Expected prior to be an instance of type Gaussian")

  if s.dtype != prior.dtype:
    raise TypeError(
        "Observation sum s.dtype does not match prior dtype: %s vs. %s"
        % (s.dtype, prior.dtype))

  n = math_ops.cast(n, prior.dtype)
  sigma0_2 = math_ops.square(prior.sigma)
  sigma_2 = math_ops.square(sigma)
  sigmap_2 = 1.0/(1/sigma0_2 + n/sigma_2)
  return Gaussian(
      mu=(prior.mu/sigma0_2 + s/sigma_2) * sigmap_2,
      sigma=math_ops.sqrt(sigmap_2))


def known_sigma_predictive(prior, sigma, s, n):
  """Posterior predictive Gaussian distribution w. conjugate prior on the mean.

  This model assumes that `n` observations (with sum `s`) come from a
  Gaussian with unknown mean `mu` (described by the Gaussian `prior`)
  and known variance `sigma^2`.  The "known sigma predictive"
  is the distribution of new observations, conditioned on the existing
  observations and our prior.

  Accepts a prior Gaussian distribution object, having parameters
  `mu0` and `sigma0`, as well as known `sigma` values of the predictive
  distribution(s) (also assumed Gaussian),
  and statistical estimates `s` (the sum(s) of the observations) and
  `n` (the number(s) of observations).

  Calculates the Gaussian distribution(s) `p(x | sigma^2)`:

  ```
    p(x | sigma^2) = int N(x | mu, sigma^2) N(mu | prior.mu, prior.sigma^2) dmu
                   = N(x | prior.mu, 1/(sigma^2 + prior.sigma^2))
  ```

  Returns the predictive posterior distribution object, with parameters
  `(mu', sigma'^2)`, where:

  ```
  sigma_n^2 = 1/(1/sigma0^2 + n/sigma^2),
  mu' = (mu0/sigma0^2 + s/sigma^2) * sigma_n^2.
  sigma'^2 = sigma_n^2 + sigma^2,
  ```

  Distribution parameters from `prior`, as well as `sigma`, `s`, and `n`.
  will broadcast in the case of multidimensional sets of parameters.

  Args:
    prior: `Gaussian` object of type `dtype`:
      the prior distribution having parameters `(mu0, sigma0)`.
    sigma: tensor of type `dtype`, taking values `sigma > 0`.
      The known stddev parameter(s).
    s: Tensor of type `dtype`.  The sum(s) of observations.
    n: Tensor of type `int`.  The number(s) of observations.

  Returns:
    A new Gaussian predictive distribution object.

  Raises:
    TypeError: if dtype of `s` does not match `dtype`, or `prior` is not a
      Gaussian object.
  """
  if not isinstance(prior, Gaussian):
    raise TypeError("Expected prior to be an instance of type Gaussian")

  if s.dtype != prior.dtype:
    raise TypeError(
        "Observation sum s.dtype does not match prior dtype: %s vs. %s"
        % (s.dtype, prior.dtype))

  n = math_ops.cast(n, prior.dtype)
  sigma0_2 = math_ops.square(prior.sigma)
  sigma_2 = math_ops.square(sigma)
  sigmap_2 = 1.0/(1/sigma0_2 + n/sigma_2)
  return Gaussian(
      mu=(prior.mu/sigma0_2 + s/sigma_2) * sigmap_2,
      sigma=math_ops.sqrt(sigmap_2 + sigma_2))
