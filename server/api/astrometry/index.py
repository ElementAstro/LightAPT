# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <lightapt.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

import hashlib
import os
import server.config as c

base_url = 'http://data.astrometry.net'
astrometry_indexes = [
    {
        "filename": "index-4200-00.fits",
        "md5sum": "6cb5f043ee6613306c21d6aec5c6d041",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-00.fits",
    },
    {
        "filename": "index-4200-01.fits",
        "md5sum": "b9811253b031695857ac77f23f86f1cd",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-01.fits",
    },
    {
        "filename": "index-4200-02.fits",
        "md5sum": "6881847b8a452332bb71438825e21945",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-02.fits",
    },
    {
        "filename": "index-4200-03.fits",
        "md5sum": "2a877b598ba04649ac22d5a576f887f0",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-03.fits",
    },
    {
        "filename": "index-4200-04.fits",
        "md5sum": "3d87dec3eebc66c72cbbf5841961eede",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-04.fits",
    },
    {
        "filename": "index-4200-05.fits",
        "md5sum": "c783cb39fe463145a27e3a2559d28232",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-05.fits",
    },
    {
        "filename": "index-4200-06.fits",
        "md5sum": "6d1158dba67e7d78bcf5ac780d342775",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-06.fits",
    },
    {
        "filename": "index-4200-07.fits",
        "md5sum": "d30823fe9e77064fc3158dec0640e799",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-07.fits",
    },
    {
        "filename": "index-4200-08.fits",
        "md5sum": "42f4b0d1a2edfe53f521848da02ebe3c",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-08.fits",
    },
    {
        "filename": "index-4200-09.fits",
        "md5sum": "92f55f6ff52828549c25b0d5716edb05",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-09.fits",
    },
    {
        "filename": "index-4200-10.fits",
        "md5sum": "60cb7b10f69e92764f924738b4efaf59",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-10.fits",
    },
    {
        "filename": "index-4200-11.fits",
        "md5sum": "822f02f7544260734f5230f69e640b07",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-11.fits",
    },
    {
        "filename": "index-4200-12.fits",
        "md5sum": "f34e76e370b558f8e6841b3d571694ea",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-12.fits",
    },
    {
        "filename": "index-4200-13.fits",
        "md5sum": "8adc6b8ecba07696ccffc351915f9e24",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-13.fits",
    },
    {
        "filename": "index-4200-14.fits",
        "md5sum": "ce55508bd136bfe18e8ec89e1bc476ae",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-14.fits",
    },
    {
        "filename": "index-4200-15.fits",
        "md5sum": "1684cf6c8c491f73ed381d544628c593",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-15.fits",
    },
    {
        "filename": "index-4200-16.fits",
        "md5sum": "32b93fcfcdcf57024df30686a579ccc0",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-16.fits",
    },
    {
        "filename": "index-4200-17.fits",
        "md5sum": "239a50a04886f011b648aaee9af5c097",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-17.fits",
    },
    {
        "filename": "index-4200-18.fits",
        "md5sum": "2e7ba028db0356b4f16af0690e821343",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-18.fits",
    },
    {
        "filename": "index-4200-19.fits",
        "md5sum": "a46c0e114c988553b6e48f0942ed2a8e",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-19.fits",
    },
    {
        "filename": "index-4200-20.fits",
        "md5sum": "9a7371de137b80ee61852bac499f9d2a",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-20.fits",
    },
    {
        "filename": "index-4200-21.fits",
        "md5sum": "beb763b3395b367e98bb8ab19ab58e6e",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-21.fits",
    },
    {
        "filename": "index-4200-22.fits",
        "md5sum": "5c2ab7de3bf3d91ac94cefbf8ce015dc",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-22.fits",
    },
    {
        "filename": "index-4200-23.fits",
        "md5sum": "5804c9785d10160e16a62127b7d6dbee",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-23.fits",
    },
    {
        "filename": "index-4200-24.fits",
        "md5sum": "61c74ad4d23db9048d4090aca78455b6",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-24.fits",
    },
    {
        "filename": "index-4200-25.fits",
        "md5sum": "bafc9b11dfc3a8bd7540296d8b7cf539",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-25.fits",
    },
    {
        "filename": "index-4200-26.fits",
        "md5sum": "f0efd6044a19329503b77b739b7f9010",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-26.fits",
    },
    {
        "filename": "index-4200-27.fits",
        "md5sum": "5576061cddadf098af0e51ea50d30b11",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-27.fits",
    },
    {
        "filename": "index-4200-28.fits",
        "md5sum": "065e39cc533a7703eb3096501fa5b633",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-28.fits",
    },
    {
        "filename": "index-4200-29.fits",
        "md5sum": "4391137f1ee5d30409e5725f7b4c0829",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-29.fits",
    },
    {
        "filename": "index-4200-30.fits",
        "md5sum": "631bd3d9e1d77a96af58d8a5214f5e0f",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-30.fits",
    },
    {
        "filename": "index-4200-31.fits",
        "md5sum": "3b977bed6474f87b927df014d6ac8bfd",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-31.fits",
    },
    {
        "filename": "index-4200-32.fits",
        "md5sum": "9471a132fcc8b67d259f003ea955f624",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-32.fits",
    },
    {
        "filename": "index-4200-33.fits",
        "md5sum": "cb672376ca5244000fa863345d97d0ab",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-33.fits",
    },
    {
        "filename": "index-4200-34.fits",
        "md5sum": "043ea32c27a649804f6576c8fd2da80c",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-34.fits",
    },
    {
        "filename": "index-4200-35.fits",
        "md5sum": "5079f6a83ace96c0202e9b4202681c96",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-35.fits",
    },
    {
        "filename": "index-4200-36.fits",
        "md5sum": "07c07152af04e69a48a80d57a38c6598",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-36.fits",
    },
    {
        "filename": "index-4200-37.fits",
        "md5sum": "71812b573536af5f3062b6694af09f05",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-37.fits",
    },
    {
        "filename": "index-4200-38.fits",
        "md5sum": "890f9bbd7e5055cf2e4b656dabb0b528",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-38.fits",
    },
    {
        "filename": "index-4200-39.fits",
        "md5sum": "2c0472c2f040d992bcb87f4a9787233c",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-39.fits",
    },
    {
        "filename": "index-4200-40.fits",
        "md5sum": "9f8e7422847000485927580bb8115af3",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-40.fits",
    },
    {
        "filename": "index-4200-41.fits",
        "md5sum": "0c7c8190e320902f434be201846d5bc0",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-41.fits",
    },
    {
        "filename": "index-4200-42.fits",
        "md5sum": "7f896e88cfb8e06e3c99644cea94ec57",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-42.fits",
    },
    {
        "filename": "index-4200-43.fits",
        "md5sum": "a26d3b2e720a518cd98a8f77750737cd",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-43.fits",
    },
    {
        "filename": "index-4200-44.fits",
        "md5sum": "a6976c91403cef33743fcc61e3353f95",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-44.fits",
    },
    {
        "filename": "index-4200-45.fits",
        "md5sum": "76bb151d8232f659447eaf7c19ffc847",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-45.fits",
    },
    {
        "filename": "index-4200-46.fits",
        "md5sum": "4d51cced4fb3662f00b430169c85d997",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-46.fits",
    },
    {
        "filename": "index-4200-47.fits",
        "md5sum": "6d331a73600211d06d3b09567baf5477",
        "arcminutes": 2.0,
        "url": "http://data.astrometry.net/4200/index-4200-47.fits",
    },
    {
        "filename": "index-4201-00.fits",
        "md5sum": "cb4ed800dba60ad4246f41581b7275b8",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-00.fits",
    },
    {
        "filename": "index-4201-01.fits",
        "md5sum": "9f3b93aab0488b0f8734d6d7ef9d4fe6",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-01.fits",
    },
    {
        "filename": "index-4201-02.fits",
        "md5sum": "d7341aabdc989239114bb62e0083d55f",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-02.fits",
    },
    {
        "filename": "index-4201-03.fits",
        "md5sum": "199b57413fffd1ddcbfce168b7fe006d",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-03.fits",
    },
    {
        "filename": "index-4201-04.fits",
        "md5sum": "8c8be944661b238e41a00076d8c23ef5",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-04.fits",
    },
    {
        "filename": "index-4201-05.fits",
        "md5sum": "0187c2749481a529531c466358c3a6ca",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-05.fits",
    },
    {
        "filename": "index-4201-06.fits",
        "md5sum": "5c568fe64f452930f44a56075dbf96d6",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-06.fits",
    },
    {
        "filename": "index-4201-07.fits",
        "md5sum": "aaaa25dd6ac51ea6ca4bd56f90d2c1b9",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-07.fits",
    },
    {
        "filename": "index-4201-08.fits",
        "md5sum": "b7e07d1d3849eb853e1e0abd071b5521",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-08.fits",
    },
    {
        "filename": "index-4201-09.fits",
        "md5sum": "6363a94df0c3bdab7b46eab98d14405f",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-09.fits",
    },
    {
        "filename": "index-4201-10.fits",
        "md5sum": "221261254bbd93807b03c7fafff8eaf4",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-10.fits",
    },
    {
        "filename": "index-4201-11.fits",
        "md5sum": "cdb6a9cf3bd3be47a3b77658e63cd405",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-11.fits",
    },
    {
        "filename": "index-4201-12.fits",
        "md5sum": "1514faf71a26d54889d5845d547d15eb",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-12.fits",
    },
    {
        "filename": "index-4201-13.fits",
        "md5sum": "8e936ebc92effb7b6724abb7a1115f48",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-13.fits",
    },
    {
        "filename": "index-4201-14.fits",
        "md5sum": "a31572593e163930549e2fd9e2936291",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-14.fits",
    },
    {
        "filename": "index-4201-15.fits",
        "md5sum": "5e1e4a8b2b379c6e2fecc6b31bbf9642",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-15.fits",
    },
    {
        "filename": "index-4201-16.fits",
        "md5sum": "e824338a6235127fd9e395bc5da811b2",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-16.fits",
    },
    {
        "filename": "index-4201-17.fits",
        "md5sum": "d334202ffdc29d0d6d90c323e4e7076e",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-17.fits",
    },
    {
        "filename": "index-4201-18.fits",
        "md5sum": "7724f1669db540c1568faa097327ab3c",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-18.fits",
    },
    {
        "filename": "index-4201-19.fits",
        "md5sum": "79ad8ef1595eb93ddf6a65eb73456338",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-19.fits",
    },
    {
        "filename": "index-4201-20.fits",
        "md5sum": "f5473bca967d8f7c1f23ee8a2878864d",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-20.fits",
    },
    {
        "filename": "index-4201-21.fits",
        "md5sum": "83bb2d947d7e68c51ac09e8c4e31ef0b",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-21.fits",
    },
    {
        "filename": "index-4201-22.fits",
        "md5sum": "1c817ad1eb47b51b92e3f900d1f094b9",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-22.fits",
    },
    {
        "filename": "index-4201-23.fits",
        "md5sum": "23e97ce76a442126043dd09ef32846b3",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-23.fits",
    },
    {
        "filename": "index-4201-24.fits",
        "md5sum": "99be21b691c0894c086c1104ad7967ee",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-24.fits",
    },
    {
        "filename": "index-4201-25.fits",
        "md5sum": "71dc3850c8fcc2f35e82e3ff9c6b644f",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-25.fits",
    },
    {
        "filename": "index-4201-26.fits",
        "md5sum": "16e2a0e74dc78202bc2e2f5355f14c0f",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-26.fits",
    },
    {
        "filename": "index-4201-27.fits",
        "md5sum": "289d04f7ad6f59bff305f60878ebf5f1",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-27.fits",
    },
    {
        "filename": "index-4201-28.fits",
        "md5sum": "224a9c64480eca951fd11be3df9a5c54",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-28.fits",
    },
    {
        "filename": "index-4201-29.fits",
        "md5sum": "c0b893c5542805f01a9abbe887ba493b",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-29.fits",
    },
    {
        "filename": "index-4201-30.fits",
        "md5sum": "b91968825beae86d236d6298fb1d0ed4",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-30.fits",
    },
    {
        "filename": "index-4201-31.fits",
        "md5sum": "27a47eb0f6a957fe78bdfe94d23fcce7",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-31.fits",
    },
    {
        "filename": "index-4201-32.fits",
        "md5sum": "f5d1162381b5ecc7a1e5508eecad37e6",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-32.fits",
    },
    {
        "filename": "index-4201-33.fits",
        "md5sum": "9506dc51319a976724bbc0b94e2b5d03",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-33.fits",
    },
    {
        "filename": "index-4201-34.fits",
        "md5sum": "83e7b59cb6592ad798fa92d334198e2b",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-34.fits",
    },
    {
        "filename": "index-4201-35.fits",
        "md5sum": "85b58acf01f0f86f7c04c5ebc1ac0569",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-35.fits",
    },
    {
        "filename": "index-4201-36.fits",
        "md5sum": "4017a7993c673c1ec5edbd2e2669e0ee",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-36.fits",
    },
    {
        "filename": "index-4201-37.fits",
        "md5sum": "a1d392f083fddd6c3aff719820c18344",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-37.fits",
    },
    {
        "filename": "index-4201-38.fits",
        "md5sum": "d8fae11435932becdef34a531523538b",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-38.fits",
    },
    {
        "filename": "index-4201-39.fits",
        "md5sum": "6fb5a1030d174121d4db3483ef6274d3",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-39.fits",
    },
    {
        "filename": "index-4201-40.fits",
        "md5sum": "3bad0938c724ca522527a36c513951ce",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-40.fits",
    },
    {
        "filename": "index-4201-41.fits",
        "md5sum": "778d0417b039e9c2033335b8012fde1a",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-41.fits",
    },
    {
        "filename": "index-4201-42.fits",
        "md5sum": "9ddb1085e40fc7127aa8c4db79ebd211",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-42.fits",
    },
    {
        "filename": "index-4201-43.fits",
        "md5sum": "a6b42262dce1e0f38e92e987210eb88b",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-43.fits",
    },
    {
        "filename": "index-4201-44.fits",
        "md5sum": "5f900854625e8385b3e237d164563838",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-44.fits",
    },
    {
        "filename": "index-4201-45.fits",
        "md5sum": "87d52b55cd68044a7d85f3c9064962b6",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-45.fits",
    },
    {
        "filename": "index-4201-46.fits",
        "md5sum": "2d666889264831b206c511c7b3967ed0",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-46.fits",
    },
    {
        "filename": "index-4201-47.fits",
        "md5sum": "6f9aaf37657097b76a803aac3fd71243",
        "arcminutes": 2.8,
        "url": "http://data.astrometry.net/4200/index-4201-47.fits",
    },
    {
        "filename": "index-4202-00.fits",
        "md5sum": "ef5a71bd24b382bb357cdac0b0ce8654",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-00.fits",
    },
    {
        "filename": "index-4202-01.fits",
        "md5sum": "6ab2c7948f24d15e794e1000853b5cd2",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-01.fits",
    },
    {
        "filename": "index-4202-02.fits",
        "md5sum": "3ff2aee78a1e50de2cda8bc083f07475",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-02.fits",
    },
    {
        "filename": "index-4202-03.fits",
        "md5sum": "8bfadff2fa58d20d217c5bc8c1f60bbd",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-03.fits",
    },
    {
        "filename": "index-4202-04.fits",
        "md5sum": "941a1e7785759fea19f4188b0a6a9a37",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-04.fits",
    },
    {
        "filename": "index-4202-05.fits",
        "md5sum": "544302040f13ec81dc01657f6b1432df",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-05.fits",
    },
    {
        "filename": "index-4202-06.fits",
        "md5sum": "6684698d518d503c06a3329e20834b73",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-06.fits",
    },
    {
        "filename": "index-4202-07.fits",
        "md5sum": "05d313118565d0544d933075853dbab1",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-07.fits",
    },
    {
        "filename": "index-4202-08.fits",
        "md5sum": "c5169b7aba239551c0b936380d545aa0",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-08.fits",
    },
    {
        "filename": "index-4202-09.fits",
        "md5sum": "d693d40a270f9013cab23edd50293afb",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-09.fits",
    },
    {
        "filename": "index-4202-10.fits",
        "md5sum": "db742a45ce2bc02cca1a65cbbdd83a48",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-10.fits",
    },
    {
        "filename": "index-4202-11.fits",
        "md5sum": "66980cf1b678c2b2a6df82d636c82823",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-11.fits",
    },
    {
        "filename": "index-4202-12.fits",
        "md5sum": "92a15d3cc0c1662d97388f69951b215b",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-12.fits",
    },
    {
        "filename": "index-4202-13.fits",
        "md5sum": "ac98621888fb0a923344c76b34b2f025",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-13.fits",
    },
    {
        "filename": "index-4202-14.fits",
        "md5sum": "e6f41bf36dfdb83a1e7e927b0374a876",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-14.fits",
    },
    {
        "filename": "index-4202-15.fits",
        "md5sum": "47cb9a762800ac5f7a054717cd35176b",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-15.fits",
    },
    {
        "filename": "index-4202-16.fits",
        "md5sum": "7d1b0d5ab112bad7c0800aa2ceda3cf1",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-16.fits",
    },
    {
        "filename": "index-4202-17.fits",
        "md5sum": "217bfc629173e018cd7cae690c062019",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-17.fits",
    },
    {
        "filename": "index-4202-18.fits",
        "md5sum": "0127bb6814aea016c855f3e4bbca0d19",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-18.fits",
    },
    {
        "filename": "index-4202-19.fits",
        "md5sum": "e1fc1f11bb0046de98924d053850ec02",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-19.fits",
    },
    {
        "filename": "index-4202-20.fits",
        "md5sum": "68c74f207c052d4f6098ba2cd2c9de15",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-20.fits",
    },
    {
        "filename": "index-4202-21.fits",
        "md5sum": "42c95dae99914f2a2ee17f46791da0d4",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-21.fits",
    },
    {
        "filename": "index-4202-22.fits",
        "md5sum": "c22ad52358469df01774551f7e52a0fc",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-22.fits",
    },
    {
        "filename": "index-4202-23.fits",
        "md5sum": "407ba0618105eac82b09915e2762ff12",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-23.fits",
    },
    {
        "filename": "index-4202-24.fits",
        "md5sum": "5ee4e8a7cbaad923e3d3b066cd992f36",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-24.fits",
    },
    {
        "filename": "index-4202-25.fits",
        "md5sum": "cce43310e71cab55df914675801c008d",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-25.fits",
    },
    {
        "filename": "index-4202-26.fits",
        "md5sum": "0c87c9dd931341e4c7a45b52b313a1fb",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-26.fits",
    },
    {
        "filename": "index-4202-27.fits",
        "md5sum": "f51bd5a1eb5286b6c23f568e610c65c8",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-27.fits",
    },
    {
        "filename": "index-4202-28.fits",
        "md5sum": "0567e9a8d19008556441c8e653bd6aef",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-28.fits",
    },
    {
        "filename": "index-4202-29.fits",
        "md5sum": "9dbcdb3e64688a5a6f439d1c8e321c5b",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-29.fits",
    },
    {
        "filename": "index-4202-30.fits",
        "md5sum": "be89b8215779416a4bb554e84c464cc9",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-30.fits",
    },
    {
        "filename": "index-4202-31.fits",
        "md5sum": "19f92d783215d40b23e9542c5502775f",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-31.fits",
    },
    {
        "filename": "index-4202-32.fits",
        "md5sum": "1c1b9e26ea76690a7cafd7d0c73c1bc8",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-32.fits",
    },
    {
        "filename": "index-4202-33.fits",
        "md5sum": "37d22e1d79391343b8deb7f8279938da",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-33.fits",
    },
    {
        "filename": "index-4202-34.fits",
        "md5sum": "a82668feff833182ad3ee0d183320c5e",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-34.fits",
    },
    {
        "filename": "index-4202-35.fits",
        "md5sum": "1b4cc661c394fae1cb2f87f42121fca5",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-35.fits",
    },
    {
        "filename": "index-4202-36.fits",
        "md5sum": "77aeb35d00bde46abdc5a89e1f751a01",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-36.fits",
    },
    {
        "filename": "index-4202-37.fits",
        "md5sum": "c765d040c5472b68ae9f2dbabc051a00",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-37.fits",
    },
    {
        "filename": "index-4202-38.fits",
        "md5sum": "d90259e4444bfdffe92e77d267f1ad9a",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-38.fits",
    },
    {
        "filename": "index-4202-39.fits",
        "md5sum": "0044a8f79ce2aa6182b99db82514401d",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-39.fits",
    },
    {
        "filename": "index-4202-40.fits",
        "md5sum": "0a52133226b38eac139cfc63069a91ee",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-40.fits",
    },
    {
        "filename": "index-4202-41.fits",
        "md5sum": "5d5c442275e3f08e71756aea8a28f608",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-41.fits",
    },
    {
        "filename": "index-4202-42.fits",
        "md5sum": "16117481f45f6a4636a5d43ff144e05c",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-42.fits",
    },
    {
        "filename": "index-4202-43.fits",
        "md5sum": "fc9b34016e5b27fdba27b1191dff5a3c",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-43.fits",
    },
    {
        "filename": "index-4202-44.fits",
        "md5sum": "ebde7203fa6ed67d3feba41053ebdad4",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-44.fits",
    },
    {
        "filename": "index-4202-45.fits",
        "md5sum": "18fbfc7142f9a3900110d211b4a92eaa",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-45.fits",
    },
    {
        "filename": "index-4202-46.fits",
        "md5sum": "9f882e372fb39743ed404f35b81b84eb",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-46.fits",
    },
    {
        "filename": "index-4202-47.fits",
        "md5sum": "80bc34e94f0d3cb2a8c7b97d35683450",
        "arcminutes": 4.0,
        "url": "http://data.astrometry.net/4200/index-4202-47.fits",
    },
    {
        "filename": "index-4203-00.fits",
        "md5sum": "ee059e006a719ccceb7696a2be29257d",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-00.fits",
    },
    {
        "filename": "index-4203-01.fits",
        "md5sum": "175e610b05d518672c9192b07ee8e258",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-01.fits",
    },
    {
        "filename": "index-4203-02.fits",
        "md5sum": "396d9cca24ce1ee8f39b46585a78e92e",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-02.fits",
    },
    {
        "filename": "index-4203-03.fits",
        "md5sum": "734ba7fd44bdc2696aab5333067522d3",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-03.fits",
    },
    {
        "filename": "index-4203-04.fits",
        "md5sum": "e6e7dba53edd5455338f6aa84f8aadc5",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-04.fits",
    },
    {
        "filename": "index-4203-05.fits",
        "md5sum": "8fd39a6c0d4094cdd432a95358f50195",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-05.fits",
    },
    {
        "filename": "index-4203-06.fits",
        "md5sum": "f01f8dfafba623428e6fd1fa20f1b60a",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-06.fits",
    },
    {
        "filename": "index-4203-07.fits",
        "md5sum": "e334101d4169ce07125adb7c0521d3f9",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-07.fits",
    },
    {
        "filename": "index-4203-08.fits",
        "md5sum": "aa0b52e94f774ecb67366c2b3e15e5e2",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-08.fits",
    },
    {
        "filename": "index-4203-09.fits",
        "md5sum": "1e191868dbf0cbb1963f2a3c056a1fd1",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-09.fits",
    },
    {
        "filename": "index-4203-10.fits",
        "md5sum": "149d645aea611dc9d6e696fb339bc430",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-10.fits",
    },
    {
        "filename": "index-4203-11.fits",
        "md5sum": "0d51797943af6158746b07786c8917d8",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-11.fits",
    },
    {
        "filename": "index-4203-12.fits",
        "md5sum": "43e106c7d84d59fa5b4d35944fdb7a9a",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-12.fits",
    },
    {
        "filename": "index-4203-13.fits",
        "md5sum": "391505c99f8ee3ab5045f152d7ae4eb2",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-13.fits",
    },
    {
        "filename": "index-4203-14.fits",
        "md5sum": "1730ff70b3e8e1914e8da13caaf22495",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-14.fits",
    },
    {
        "filename": "index-4203-15.fits",
        "md5sum": "867fb56676d09a5a31140aa0efc85895",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-15.fits",
    },
    {
        "filename": "index-4203-16.fits",
        "md5sum": "4758c64318d0583fdb03717d59df15be",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-16.fits",
    },
    {
        "filename": "index-4203-17.fits",
        "md5sum": "977dd7a62ad93d6281ca53cc500ae429",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-17.fits",
    },
    {
        "filename": "index-4203-18.fits",
        "md5sum": "82ed3702bf8dc4fbdfe629f67cc541c4",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-18.fits",
    },
    {
        "filename": "index-4203-19.fits",
        "md5sum": "f234a828e81762673209d12ccc453fb7",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-19.fits",
    },
    {
        "filename": "index-4203-20.fits",
        "md5sum": "608c17e90e1413ce93ad84e7cb954e3d",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-20.fits",
    },
    {
        "filename": "index-4203-21.fits",
        "md5sum": "74a72f655e3799ddf104715cc1fb75ee",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-21.fits",
    },
    {
        "filename": "index-4203-22.fits",
        "md5sum": "5e4c327d08609cf45798ea46a7b11e56",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-22.fits",
    },
    {
        "filename": "index-4203-23.fits",
        "md5sum": "604a89d5f1c68bcf633cdbb1aa2caf7c",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-23.fits",
    },
    {
        "filename": "index-4203-24.fits",
        "md5sum": "8a3be15c995d938f6a11e3f0e113ef74",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-24.fits",
    },
    {
        "filename": "index-4203-25.fits",
        "md5sum": "6c82762dcdd489868b4b87961eae47c7",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-25.fits",
    },
    {
        "filename": "index-4203-26.fits",
        "md5sum": "5dca9b3901cb1e96d7be4a227e877c7e",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-26.fits",
    },
    {
        "filename": "index-4203-27.fits",
        "md5sum": "fca9e3ca8cab308f164b8a8685bd3baa",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-27.fits",
    },
    {
        "filename": "index-4203-28.fits",
        "md5sum": "6956a4c32c58520bf594e02877a44620",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-28.fits",
    },
    {
        "filename": "index-4203-29.fits",
        "md5sum": "709965eab3906499152f2149c3d41398",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-29.fits",
    },
    {
        "filename": "index-4203-30.fits",
        "md5sum": "ff44f6f683d3cbb3c040ba89e297c558",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-30.fits",
    },
    {
        "filename": "index-4203-31.fits",
        "md5sum": "c619bac89bc35d2b8ba9ac25c4259aa7",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-31.fits",
    },
    {
        "filename": "index-4203-32.fits",
        "md5sum": "335101fc751f5937c94f805f891f8685",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-32.fits",
    },
    {
        "filename": "index-4203-33.fits",
        "md5sum": "c505e59b27853aaf9b7cf33dedf1e7f0",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-33.fits",
    },
    {
        "filename": "index-4203-34.fits",
        "md5sum": "14684a843d50a795ab97dc0b4c063d01",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-34.fits",
    },
    {
        "filename": "index-4203-35.fits",
        "md5sum": "d38711209387ae1566c88f2a6eebd2fe",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-35.fits",
    },
    {
        "filename": "index-4203-36.fits",
        "md5sum": "e164bd26e8b5440c8aba4c3c4178809f",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-36.fits",
    },
    {
        "filename": "index-4203-37.fits",
        "md5sum": "067c3b0b3153863e1430f5767feb39d9",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-37.fits",
    },
    {
        "filename": "index-4203-38.fits",
        "md5sum": "1108c767d23efb7bb53337fbf7b3d155",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-38.fits",
    },
    {
        "filename": "index-4203-39.fits",
        "md5sum": "09c29489e9fbc1dd5ec6e9f62b7a2b64",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-39.fits",
    },
    {
        "filename": "index-4203-40.fits",
        "md5sum": "607ba03cddacbc673ac5404132e5678a",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-40.fits",
    },
    {
        "filename": "index-4203-41.fits",
        "md5sum": "4b2999cd398697dab8511d9e830ae0bf",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-41.fits",
    },
    {
        "filename": "index-4203-42.fits",
        "md5sum": "381a4a9c7f051ac00388657a4242bdb8",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-42.fits",
    },
    {
        "filename": "index-4203-43.fits",
        "md5sum": "9269dacfd3609e48c721b00b14f24a5c",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-43.fits",
    },
    {
        "filename": "index-4203-44.fits",
        "md5sum": "22d54cd920d9aa88366dcf63e6ed14fb",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-44.fits",
    },
    {
        "filename": "index-4203-45.fits",
        "md5sum": "8e6cf4a868e087c4878232f4548ae65c",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-45.fits",
    },
    {
        "filename": "index-4203-46.fits",
        "md5sum": "440bae39994d6b0b9a782c1203ee7f90",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-46.fits",
    },
    {
        "filename": "index-4203-47.fits",
        "md5sum": "c5adeffd16aee06ba68288cae9af2c3f",
        "arcminutes": 5.6,
        "url": "http://data.astrometry.net/4200/index-4203-47.fits",
    },
    {
        "filename": "index-4204-00.fits",
        "md5sum": "43e3049c13c98563ca5abfd8589e8a6c",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-00.fits",
    },
    {
        "filename": "index-4204-01.fits",
        "md5sum": "738a8b91ac99d74d3ab8c1cf7a479152",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-01.fits",
    },
    {
        "filename": "index-4204-02.fits",
        "md5sum": "1122eb86dd21f503d4a0ab2d9d3fd681",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-02.fits",
    },
    {
        "filename": "index-4204-03.fits",
        "md5sum": "c31a0210d48f99275da5a014a7d3a1cd",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-03.fits",
    },
    {
        "filename": "index-4204-04.fits",
        "md5sum": "837182ea240a1733f9ebece4cea30fe8",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-04.fits",
    },
    {
        "filename": "index-4204-05.fits",
        "md5sum": "6b415298a9418d59ff952e2438ef2fbd",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-05.fits",
    },
    {
        "filename": "index-4204-06.fits",
        "md5sum": "2d5a0352eac0cd3bdb436dbbc14120cc",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-06.fits",
    },
    {
        "filename": "index-4204-07.fits",
        "md5sum": "f1f9ccf4f03fd59573dedc28b95e3124",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-07.fits",
    },
    {
        "filename": "index-4204-08.fits",
        "md5sum": "3cdff77454b95df95051ff0de8a8736b",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-08.fits",
    },
    {
        "filename": "index-4204-09.fits",
        "md5sum": "ddbd58e7bde99dfb9459735f48700adc",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-09.fits",
    },
    {
        "filename": "index-4204-10.fits",
        "md5sum": "3a12c567d58a2a26bb5c2d288bb0be59",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-10.fits",
    },
    {
        "filename": "index-4204-11.fits",
        "md5sum": "52663a7b92efad0ece6bfd0222b645fb",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-11.fits",
    },
    {
        "filename": "index-4204-12.fits",
        "md5sum": "931660e7ab8eeb193ff95ff5c8a832b3",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-12.fits",
    },
    {
        "filename": "index-4204-13.fits",
        "md5sum": "f05ba6f64aad32992656fbafd2bc2b15",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-13.fits",
    },
    {
        "filename": "index-4204-14.fits",
        "md5sum": "39eb81b54dc307f96c2b0c72d987903b",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-14.fits",
    },
    {
        "filename": "index-4204-15.fits",
        "md5sum": "b643670e452327b6568429389d15c2b1",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-15.fits",
    },
    {
        "filename": "index-4204-16.fits",
        "md5sum": "01624f2ea855be3b60ba63116b95d926",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-16.fits",
    },
    {
        "filename": "index-4204-17.fits",
        "md5sum": "d2c146bee92438f1c585908b6e9a613b",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-17.fits",
    },
    {
        "filename": "index-4204-18.fits",
        "md5sum": "59be7a21ef214443f7eb23d503a202ad",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-18.fits",
    },
    {
        "filename": "index-4204-19.fits",
        "md5sum": "9c34ed4e2a4efed350edc201dc9fb1fd",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-19.fits",
    },
    {
        "filename": "index-4204-20.fits",
        "md5sum": "c12a8eb9e04a371a03b771fbe151575d",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-20.fits",
    },
    {
        "filename": "index-4204-21.fits",
        "md5sum": "df1b2f9767e1b23303dd60f1b8e39e4b",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-21.fits",
    },
    {
        "filename": "index-4204-22.fits",
        "md5sum": "d040798ce5417cdb78e675f1d0b30857",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-22.fits",
    },
    {
        "filename": "index-4204-23.fits",
        "md5sum": "0f25e3872caba1a01810d80ccb4b7798",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-23.fits",
    },
    {
        "filename": "index-4204-24.fits",
        "md5sum": "993012cc037c3e8cfa2412f1bd0f9926",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-24.fits",
    },
    {
        "filename": "index-4204-25.fits",
        "md5sum": "02a6ae14cbf68e6fb7d2c8bb1b0c9ec2",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-25.fits",
    },
    {
        "filename": "index-4204-26.fits",
        "md5sum": "c7dec9bda5132a79236c2a7be8ed395d",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-26.fits",
    },
    {
        "filename": "index-4204-27.fits",
        "md5sum": "55442517d36d6fef2709e209111e69b5",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-27.fits",
    },
    {
        "filename": "index-4204-28.fits",
        "md5sum": "3910ff38dc528b7cd1e0803cbc14c80c",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-28.fits",
    },
    {
        "filename": "index-4204-29.fits",
        "md5sum": "c6a6ed56b5602d888477267f3d44ce77",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-29.fits",
    },
    {
        "filename": "index-4204-30.fits",
        "md5sum": "5f48f81e511858afdd7b303a6144e385",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-30.fits",
    },
    {
        "filename": "index-4204-31.fits",
        "md5sum": "e3e3deed3bfba8a6b0f53011cd0ac8b9",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-31.fits",
    },
    {
        "filename": "index-4204-32.fits",
        "md5sum": "ffc5493828665f6e6b4da5b8b987c5d2",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-32.fits",
    },
    {
        "filename": "index-4204-33.fits",
        "md5sum": "f206556da41752a7922ef1e4a87377c6",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-33.fits",
    },
    {
        "filename": "index-4204-34.fits",
        "md5sum": "50bc7534ccb9e2f7ca21790434c4a290",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-34.fits",
    },
    {
        "filename": "index-4204-35.fits",
        "md5sum": "fa4506a71d7ae2f26165a29e4daccae0",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-35.fits",
    },
    {
        "filename": "index-4204-36.fits",
        "md5sum": "77a39ddea411c08b6cfa780c8e8d83ee",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-36.fits",
    },
    {
        "filename": "index-4204-37.fits",
        "md5sum": "861bbc3951473fb4d5c0dd2aaac22b3b",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-37.fits",
    },
    {
        "filename": "index-4204-38.fits",
        "md5sum": "d7808bfa079e20cfe917c0804485455e",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-38.fits",
    },
    {
        "filename": "index-4204-39.fits",
        "md5sum": "06566a8c639a2638f6793e94871e4acb",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-39.fits",
    },
    {
        "filename": "index-4204-40.fits",
        "md5sum": "3d5b33845c8a5e97ebb6efe67dbebd46",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-40.fits",
    },
    {
        "filename": "index-4204-41.fits",
        "md5sum": "104385a4dc2ad0a9ed0f3f848856a667",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-41.fits",
    },
    {
        "filename": "index-4204-42.fits",
        "md5sum": "5c49500ffce437ea6b84c793f2559181",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-42.fits",
    },
    {
        "filename": "index-4204-43.fits",
        "md5sum": "57221ed3e7e2610dfab10d0971ea6955",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-43.fits",
    },
    {
        "filename": "index-4204-44.fits",
        "md5sum": "b7dbe51a7171ef016c9276ed2556eca6",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-44.fits",
    },
    {
        "filename": "index-4204-45.fits",
        "md5sum": "a8e866b3c89a8ae6e0f8c76f9f369655",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-45.fits",
    },
    {
        "filename": "index-4204-46.fits",
        "md5sum": "bac788ab3755ca7d75a349a205cb1528",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-46.fits",
    },
    {
        "filename": "index-4204-47.fits",
        "md5sum": "950dbecea2a98b3a2f0b83bad9f70365",
        "arcminutes": 8,
        "url": "http://data.astrometry.net/4200/index-4204-47.fits",
    },
    {
        "filename": "index-4205-00.fits",
        "md5sum": "920b54f14b5ee68780e4f5e1f1132def",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-00.fits",
    },
    {
        "filename": "index-4205-01.fits",
        "md5sum": "0674bc153e2d58f9cbd3fbbd8ee35032",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-01.fits",
    },
    {
        "filename": "index-4205-02.fits",
        "md5sum": "f1f9bfa549abd40d731a3d8382488045",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-02.fits",
    },
    {
        "filename": "index-4205-03.fits",
        "md5sum": "d5a7b993523062886d17af938648d73d",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-03.fits",
    },
    {
        "filename": "index-4205-04.fits",
        "md5sum": "18b947879cd49e80d970cb76ab07af77",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-04.fits",
    },
    {
        "filename": "index-4205-05.fits",
        "md5sum": "2e66e17b97083adb0e41b54819c5cfa2",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-05.fits",
    },
    {
        "filename": "index-4205-06.fits",
        "md5sum": "abd741644bcde142c845ce0b2d1b3791",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-06.fits",
    },
    {
        "filename": "index-4205-07.fits",
        "md5sum": "c55714dd1f27a74adfa2c9937dc00138",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-07.fits",
    },
    {
        "filename": "index-4205-08.fits",
        "md5sum": "07ad195476c2115d73ba7df902c93e61",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-08.fits",
    },
    {
        "filename": "index-4205-09.fits",
        "md5sum": "dbd8513c6c328b7275302e50144f62b8",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-09.fits",
    },
    {
        "filename": "index-4205-10.fits",
        "md5sum": "baca0a586ff36d8345eaff3a6c8c071b",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-10.fits",
    },
    {
        "filename": "index-4205-11.fits",
        "md5sum": "894ccdbd9d8b2ac69693bd7d9862e8aa",
        "arcminutes": 11,
        "url": "http://data.astrometry.net/4200/index-4205-11.fits",
    },
    {
        "filename": "index-4206-00.fits",
        "md5sum": "d346096ad3218f8694a2676931f98c10",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-00.fits",
    },
    {
        "filename": "index-4206-01.fits",
        "md5sum": "277d7da550aba6b717df1311cd90c963",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-01.fits",
    },
    {
        "filename": "index-4206-02.fits",
        "md5sum": "f5ce1aa735b06ec984462671ef6bc66e",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-02.fits",
    },
    {
        "filename": "index-4206-03.fits",
        "md5sum": "d0605eddd4544a445627e6e4ae2a8a1f",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-03.fits",
    },
    {
        "filename": "index-4206-04.fits",
        "md5sum": "a49e82c7ea88d0c3a45b36da52619d3a",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-04.fits",
    },
    {
        "filename": "index-4206-05.fits",
        "md5sum": "d987c5c2def80789862a56bdd8a2a00c",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-05.fits",
    },
    {
        "filename": "index-4206-06.fits",
        "md5sum": "f6c5d6da3844984d33d591e72833625a",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-06.fits",
    },
    {
        "filename": "index-4206-07.fits",
        "md5sum": "cbf7ba26681274d9c3490541fac1610a",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-07.fits",
    },
    {
        "filename": "index-4206-08.fits",
        "md5sum": "3772dccbc198ad851564a17ca14944b3",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-08.fits",
    },
    {
        "filename": "index-4206-09.fits",
        "md5sum": "65514ddc576316efaf554fff505cae20",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-09.fits",
    },
    {
        "filename": "index-4206-10.fits",
        "md5sum": "c9b87d5a64265e4db5a5852351d2c159",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-10.fits",
    },
    {
        "filename": "index-4206-11.fits",
        "md5sum": "cb461080181a2aa6e9114266a842d26e",
        "arcminutes": 16,
        "url": "http://data.astrometry.net/4200/index-4206-11.fits",
    },
    {
        "filename": "index-4207-00.fits",
        "md5sum": "13b65b37d5ceca7278a98ad4779cc5f7",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-00.fits",
    },
    {
        "filename": "index-4207-01.fits",
        "md5sum": "d9a2a92e3106ff09b1b6efab18e47488",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-01.fits",
    },
    {
        "filename": "index-4207-02.fits",
        "md5sum": "ab339cbd34534a4075752eb046be2a85",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-02.fits",
    },
    {
        "filename": "index-4207-03.fits",
        "md5sum": "a25cb3f103be06b7908e195996a1e624",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-03.fits",
    },
    {
        "filename": "index-4207-04.fits",
        "md5sum": "030b91123b6f338bffb214dc20fbb723",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-04.fits",
    },
    {
        "filename": "index-4207-05.fits",
        "md5sum": "0aa51a0b2bbe5b6a9e1f539060cbbcbf",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-05.fits",
    },
    {
        "filename": "index-4207-06.fits",
        "md5sum": "234948c09eab7ef42c5558b475031980",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-06.fits",
    },
    {
        "filename": "index-4207-07.fits",
        "md5sum": "37267d6d302444b548239bcc68c18b16",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-07.fits",
    },
    {
        "filename": "index-4207-08.fits",
        "md5sum": "341c662971c9f1368619baf491c5d59c",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-08.fits",
    },
    {
        "filename": "index-4207-09.fits",
        "md5sum": "1f2d7c9847a05ce3d741eb35cee19988",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-09.fits",
    },
    {
        "filename": "index-4207-10.fits",
        "md5sum": "3d07b8e27d8a6fd5801aa6bef2b17dc2",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-10.fits",
    },
    {
        "filename": "index-4207-11.fits",
        "md5sum": "fb88bf437d6a39082534da13048ff0bd",
        "arcminutes": 22,
        "url": "http://data.astrometry.net/4200/index-4207-11.fits",
    },
    {
        "filename": "index-4208.fits",
        "md5sum": "815a5a4d1d234376453ba3372f473859",
        "arcminutes": 30,
        "url": "http://data.astrometry.net/4200/index-4208.fits",
    },
    {
        "filename": "index-4209.fits",
        "md5sum": "764db3e2d62c24e2674fa519003c95a2",
        "arcminutes": 42,
        "url": "http://data.astrometry.net/4200/index-4209.fits",
    },
    {
        "filename": "index-4210.fits",
        "md5sum": "1e4e04320b7a188b6a8618060096d52b",
        "arcminutes": 60,
        "url": "http://data.astrometry.net/4200/index-4210.fits",
    },
    {
        "filename": "index-4211.fits",
        "md5sum": "a1d1ef557482cf9f9003c74a5c6dad66",
        "arcminutes": 85,
        "url": "http://data.astrometry.net/4200/index-4211.fits",
    },
    {
        "filename": "index-4212.fits",
        "md5sum": "ae1b8ea7628ffe109f3595ea566c4f6f",
        "arcminutes": 120,
        "url": "http://data.astrometry.net/4200/index-4212.fits",
    },
    {
        "filename": "index-4213.fits",
        "md5sum": "2573d536f83596ebaf58ea4d30091e1b",
        "arcminutes": 170,
        "url": "http://data.astrometry.net/4200/index-4213.fits",
    },
    {
        "filename": "index-4214.fits",
        "md5sum": "befdfa0ccf520f0113d54fe88a2721aa",
        "arcminutes": 240,
        "url": "http://data.astrometry.net/4200/index-4214.fits",
    },
    {
        "filename": "index-4215.fits",
        "md5sum": "2ffdbb967d94ea7677bbf61cf126727b",
        "arcminutes": 340,
        "url": "http://data.astrometry.net/4200/index-4215.fits",
    },
    {
        "filename": "index-4216.fits",
        "md5sum": "6aa8013950d0f69416c29b0e1f6678b3",
        "arcminutes": 480,
        "url": "http://data.astrometry.net/4200/index-4216.fits",
    },
    {
        "filename": "index-4217.fits",
        "md5sum": "28877a3da074f948ceaec51e83231aa3",
        "arcminutes": 680,
        "url": "http://data.astrometry.net/4200/index-4217.fits",
    },
    {
        "filename": "index-4218.fits",
        "md5sum": "4505d4005f19bdb6ca71fb3bb52e6adf",
        "arcminutes": 1000,
        "url": "http://data.astrometry.net/4200/index-4218.fits",
    },
    {
        "filename": "index-4219.fits",
        "md5sum": "4346ea1a93d9c39bdc07de8abdde4915",
        "arcminutes": 1400,
        "url": "http://data.astrometry.net/4200/index-4219.fits",
    },
]

astrometry_indexes_tycho = [
    {
        'filename': 'index-4107.fits',
        'md5sum': 'f963cdd3bae5aa985d2245464ef444d6',
        'url': 'http://data.astrometry.net/4100/index-4107.fits'
    },
    {
        'filename': 'index-4108.fits',
        'md5sum': 'e6a3a643fa06cbbdf1dee478e4d84a32',
        'url': 'http://data.astrometry.net/4100/index-4108.fits'
    },
    {
        'filename': 'index-4109.fits',
        'md5sum': '9a65a52ce04e3e75af950e5866f81b1b',
        'url': 'http://data.astrometry.net/4100/index-4109.fits'
    },
    {
        'filename': 'index-4110.fits',
        'md5sum': 'd9aeb509b107d3bf8f79346329f1c0e3',
        'url': 'http://data.astrometry.net/4100/index-4110.fits'
    },
    {
        'filename': 'index-4111.fits',
        'md5sum': 'cd7c149671d92a430bbe64c046ffcac3',
        'url': 'http://data.astrometry.net/4100/index-4111.fits'
    },
    {
        'filename': 'index-4112.fits',
        'md5sum': '76568e3703f492121a1affca7368f3c2',
        'url': 'http://data.astrometry.net/4100/index-4112.fits'
    },
    {
        'filename': 'index-4113.fits',
        'md5sum': 'd36a7d5f06b0443f7951751733b1b088',
        'url': 'http://data.astrometry.net/4100/index-4113.fits'
    },
    {
        'filename': 'index-4114.fits',
        'md5sum': '0afbed8177b0e101dfc8925c5c077005',
        'url': 'http://data.astrometry.net/4100/index-4114.fits'
    },
    {
        'filename': 'index-4115.fits',
        'md5sum': '0db912aba86fa97159add4a65833ec10',
        'url': 'http://data.astrometry.net/4100/index-4115.fits'
    },
    {
        'filename': 'index-4116.fits',
        'md5sum': 'b70cb06f819144de4c659524a735f4f3',
        'url': 'http://data.astrometry.net/4100/index-4116.fits'
    },
    {
        'filename': 'index-4117.fits',
        'md5sum': 'ccf0ef3e8faac6feb0f5fb74d88a3152',
        'url': 'http://data.astrometry.net/4100/index-4117.fits'
    },
    {
        'filename': 'index-4118.fits',
        'md5sum': 'a99b85c89f16e6d1ab6dbc19d9ac1d1a',
        'url': 'http://data.astrometry.net/4100/index-4118.fits'
    },
    {
        'filename': 'index-4119.fits',
        'md5sum': '25c404b35a08558a1404d3f6145abf1c',
        'url': 'http://data.astrometry.net/4100/index-4119.fits'
    },
]

def verify_template(self, f : dict) -> bool:
    """
        Using MD5 to verify the template file
        Args:
            file_path : dict 
        Returns: bool
    """
    file_path = os.path.join(c.config["solver"]["astrometry"],f.get('filename'))
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'rb') as fileobj:
        m = hashlib.md5()
        while True:
            chunk = fileobj.read(1024)
            if not chunk:
                break
            m.update(chunk)
            md5sum = m.hexdigest()
        return md5sum == f.get('md5sum')

from ....utils.utility import Download

def download_template(filename : str) -> None:
    """
        Mutil-threads download a template
        Args:
            filename : str
        Returns: None
    """