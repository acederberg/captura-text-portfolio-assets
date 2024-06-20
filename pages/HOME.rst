.. ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
.. NOTE: DO NOT USE A TITLE! `<h1>` then uses an id that makes css a pain.
.. container:: home-0

    **Hello, I am**

.. container:: home-1 

   **Adrian Cederberg!**

.. ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
.. NOTE: Yucky image includes.

.. |commits| image:: /git.svg
   :height: 32px
   :alt: commits

.. |resume| image:: /document.svg
   :height: 32px
   :alt: resume

.. |github| image:: /github.svg
   :height: 32px
   :alt: github

.. |about| image:: /about.svg
   :height: 32px
   :alt: about

.. |projects| image:: /database.svg
   :height: 32px
   :alt: about


.. container:: home-2

   Here you can find my projects, progress, and links.

   - |github| `Github <https://github.com/acederberg>`_
   - |resume| `Resume </resume>`_
   - |about| `About This Website <#about>`_
   - |about| `About Me </about>`_
   - |commits| `Commits <#commits>`_
   - |projects| `Projects </projects>`_

.. - `Captura`


.. container:: home-3

   .. This is a filler, do not remove it. Also, do not use a title in the next 
      section.


.. raw:: html

  <a name="about"></a>


.. container:: home-about-title

   **About This Site**


.. container:: home-about-content

   The site is built from the content of `captura-text-portfolio-assets <https://github.com/acederberg/captura-text-portfolio-assets>`_ using the
   `text <https://github.com/acederberg/captura-text>`_ extension for `captura <https://github.com/acederberg/captura>`_. 
   It does nothing all too fancy, since developing an deploying a ``js``/``ts``/``pHp`` front-end (
   for instance) would be overkill for my purpose and would fail to show a use-case for ``captura``.

   All of the pages on this site are stored and served by captura, and all ``HTML``
   pages are actually rendered from restructured text.

   The ``text`` extension for captura makes it extremely simple to deploy some 
   web assets (``html``, ``css``, ``svg``, etc) to a captura instance. For the 
   moment, the `text` extension is available only for those deploying captura 
   instances. Soon users will be able to share, collaborate, and publish articles 
   using this extension.

   For more on any of these projects, see `projects`_. 


.. container:: home-3

   .. This is a filler, do not remove it. Also, do not use a title in the next 
      section.


.. raw:: html

  <a name="commits"></a>


.. container:: home-about-title

   **Commits**


.. raw:: html

  <div class="commits">
    <img 
      src=https://avatars.githubusercontent.com/u/77076023?v=4
      alt="Github profile image"
    ></img>
    <script src="https://cdn.rawgit.com/IonicaBizau/github-calendar/gh-pages/dist/github-calendar.min.js"></script>
    <link rel="stylesheet" href="/commits.css"/>

    <!-- Prepare a container for your calendar. -->
    <div class="calendar"></div>

    <script>
        new GitHubCalendar(".calendar", "acederberg", {global_stats: false, summary_text: null});
    </script>
  </div>


.. container:: home-about-content

   Calendar is powered by `IonicaBizau/github-calendar <https://github.com/Bloggify/github-calendar>`_.
   
   This is a graph of my productivity on ``github``. Keep in mind that not all 
   contributions are equal. If you want to see my contributions in detail,
   please go to `my github <https://github.com/acederberg>`_. Also, this 
   account tracks only my own contributions and does not track my contributions 
   in other platforms (e.g. Atlassian's ``bitbucket``).
  



