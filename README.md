# Akvaariosovellus

Sovellus, jolla voit pitää kirjaa akvaarioistasi ja niiden asukkaista, sekä selata muiden ihmisten lisäämiä akvaarioita.


## Ominaisuudet

- [x] Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- [x] Käyttäjä pystyy lisäämään sovellukseen akvaarioita. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään akvaarioita.
- [x] Akvaarioon voi lisätä asukkeja. Asukkeja voi muokata, poistaa ja siirtää akvaariosta toiseen.
- [x] Akvaarioon voi lisätä kuvia. Käyttäjä voi valita yhden kuvista pääkuvaksi, joka näkyy akvaarion kansikuvana.
- [x] Käyttäjä näkee sovellukseen lisätyt akvaariot. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät akvaariot.
- [x] Käyttäjä pystyy etsimään omia ja muiden akvaarioita hakusanan perusteella.
- [x] Käyttäjä pystyy etsimään/rajaamaan omia ja muiden akvaariota lajin, koon, päivämäärän ja luokkien perusteella.
- [x] Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja (akvaarioiden lukumäärä, lajien ja yksilöiden lukumäärä jne.) ja käyttäjän lisäämät akvaariot.
- [x] Käyttäjä pystyy valitsemaan akvaariolle yhden tai useamman luokittelun, esimerkiksi lämpötilan tai veden (kuten merivesi) mukaan.
- [x] Käyttäjä pystyy lisäämään kommentteja omiin ja muiden käyttäjien akvaarioihin.


## Sovelluksen käynnistäminen

*(Windows)*

1. Kloonaa repositorio komennolla `git clone https://github.com/nuoliainen/akvaariot` tai [lataa ZIP-tiedosto](https://github.com/nuoliainen/akvaariot/archive/refs/heads/main.zip) ja pura kansio.
2. Tuplaklikkaa RUN.bat tiedostoa tai syötä komentoja manuaalisesti seuraavan kuvauksen mukaisesti:
   - Luo virtuaaliympäristö komennolla `python -m venv venv`
   - Aktivoi virtuaaliympäristö komennolla `call venv\Scripts\activate`
   - Asenna Flask komennolla `pip install flask`
   - Luo tietokanta komennolla `sqlite3 database.db < schema.sql`
   - Alusta luokkatiedot komennolla `sqlite3 database.db < init.sql`
   - Suorita komento `flask run`, jonka jälkeen sovelluksen pitäisi toimia selaimella osoitteessa http://127.0.0.1:5000/


## Sovelluksen testaaminen

Suuren määrän testidataa voi halutessaan luoda tiedostolla seed.py.

1. Käynnistä sovellus (yllä olevien ohjeiden mukaisesti)
2. Avaa selain ja siirry osoitteeseen http://127.0.0.1:5000
3. Luo uusi käyttäjätunnus valitsemalla *Luo tunnus*
4. Kirjaudu sisään ja käytä sovelluksen toimintoja:
   - Lisää uusia akvaarioita
   - Muokkaa (ja poista) akvaarioita
   - Lisää eläimiä akvaariohin, sekä muokkaa ja poista niitä
   - Lisää (ja poista) kuvia, vaihda pääkuvaa
   - Lisää (ja poista) kommentteja
   - Kokeile hakutoimintoa kirjoittamalla jokin hakusana ja rajaamalla esimerkiksi jonkin luokan perusteella
   - Käy omalla ja muiden käyttäjäsivuilla
5. Kirjaudu ulos


## Suuri tietomäärä

Sovellus on testattu suurella määrällä dataa, joka luotiin tiedostolla seed.py. Lähtöarvot olivat seuraavat:

```
user_count = 1000
aquarium_count = 10**6
comment_count = 10**7
critter_count = 10**6
```

Etusivu aukeaa välittömästi (0.0-0.02s) ja sivulta seuraaville siirtyminen toimii myös hyvin. Viimeisimmille sivulle hyppääminen kuitenkin nostaa sivun latautumisaikaa noin kahteen sekuntiin, joka liittynee siihen, miten sivutus on toteutettu (`LIMIT ? OFFSET ?`). Käyttäjäsivut toimivat myös yhtä nopeasti. Akvaarion luomisessa ja muokkaamisessa sekä eläinten lisäämisessä ei ole viivettä. Tunnuksen luomisessa kuluu noin 0.11 sekuntia, mikä ei vielä häiritse käyttökokemusta.

Hakutoiminto kuitenkin toimii vaihtelevasti. Tilavuuden ja päivämäärän mukaan rajaaminen toimii alle sekunnissa. Hakusanan perusteella hamkemiseen kuluu jo lähemmäs 3 sekuntia, mutta sen tehostamiseen ei voi käyttää indeksiä, sillä kysely on muotoa `"%" + query + "%"` (alkaa %:lla). Sama ongelma on lajihaussa, joka on toteutettu samalla tavalla kuin hakusana; hakutulokset latautuvat noin 4,5 sekunnissa.

Luokkien mukaan hakutulosten rajaaminen toimii selkeästi heikoiten; jopa 7-9 sekuntia riippuen hieman paljonko tuloksia on ja montako luokkaa on valittuna. Jättämällä taulukosta aquarium_classes pois `UNIQUE(aquarium_id, title)`, haku nopeutuu muutamalla sekunnilla. Sen kanssa SQL käyttää ilmeisesti omaa indeksiään (`sqlite_autoindex_aquarium_classes_1`) itse luomani indeksin sijaan. Sen pois jättäminen ei kuitenkaan ole välttämättä hyvä idea tietokannan eheyden ylläpitämiseksi. SQL-kyselyn rakenteesta löytyisi varmasti parannettavaa.
