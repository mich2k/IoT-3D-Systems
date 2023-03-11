
import { useState, useEffect } from 'react'
import { BrowserRouter, Route, Routes } from "react-router-dom";
import home from '../home/Home';
import axios from 'axios'
import React from 'react';
import User from '../User'
import PropTypes from 'prop-types';
import { useNavigate } from "react-router-dom";
import useToken from '../../useToken';
const Login = () => {

  const { setToken } = useToken();

  const navigate = useNavigate();


  const [checked_state, setCheck] = useState(false);

  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');


  const [state_user, setUser] = useState<User>();



  const url = "https://flask.gmichele.it";



  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!checked_state) {
      console.log('check');
      return;
    }


    const data = {
      username: username,
      password: password
    }


    axios
      .post(url + '/login/loginuser', data, {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json;charset=UTF-8",
        },
      })
      .then(({ data }) => {

        console.log(data);

        const my_user = new User(username, password, data["access_token"], data["name"], data["surname"],
          data["apartment_ID"], data["internal_number"], data["city"], data["birth_year"]);

        setUser(my_user);


        navigate("/home", {
          state: { apartment_name: data["apartment_ID"], firstname: data["name"], surname: data["surname"], access_token: data["access_token"], city: data["city"], internal_number: data["internal_number"], user: my_user }
        });

      }).catch((error) => {
        console.dir(error);
      });


  }




  return (

    <section className="h-full gradient-form bg-gray-200 md:h-screen">
      <div className="container py-12 px-6 h-full">
        <div className="flex justify-center items-center flex-wrap h-full g-6 text-gray-800">
          <div className="xl:w-10/12">
            <div className="block bg-white shadow-lg rounded-lg">
              <div className="lg:flex lg:flex-wrap g-0">
                <div className="lg:w-6/12 px-4 md:px-0">
                  <div className="md:p-12 md:mx-6">
                    <div className="text-center">
                      <img
                        className="mx-auto w-48"
                        width="100px"
                        src="https://e7.pngegg.com/pngimages/165/760/png-clipart-s-s-c-napoli-2017-audi-cup-stadio-san-paolo-football-uefa-champions-league-football-ssc-napoli-2017-audi-cup.png"
                        alt="logo"
                      />
                      <h4 className="text-xl font-semibold mt-1 mb-8 pb-1">the smartest bin among the smartest.</h4>
                      <h5 className="text-l font-italic mt-1 mb-4 pb-1">Welcome, please log in </h5>
                    </div>
                    <form onSubmit={handleSubmit}>
                      <p className="mb-4">Please access with given credentials</p>
                      <div className="mb-4">
                        <input
                          type="text"
                          className="form-control block w-full px-3 py-1.5 text-base font-normal text-gray-700 bg-white bg-clip-padding border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
                          id="txt-username-field"
                          placeholder="username"
                          onChange={(e) => { setUsername(e.target.value) }}
                        />
                      </div>
                      <div className="mb-4">
                        <input
                          type="password"
                          className="form-control block w-full px-3 py-1.5 text-base font-normal text-gray-700 bg-white bg-clip-padding border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
                          id="txt-psw-field"
                          placeholder="password"
                          onChange={(e) => { setPassword(e.target.value) }}
                        />
                      </div>
                      <div className="text-center pt-1 mb-12 pb-1">
                        <button
                          className="inline-block px-6 py-2.5 text-gray font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-blue-400 hover:shadow-lg focus:shadow-lg focus:outline-none focus:ring-0 active:shadow-lg transition duration-150 ease-in-out w-full mb-3"
                          type="submit"
                          data-mdb-ripple="true"
                          data-mdb-ripple-color="light"
                        >
                          Log in
                        </button>
                        <div className="flex items-center mb-4">
                          <input onChange={() => { setCheck(!checked_state); }} id="default-checkbox" type="checkbox" value="" className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600" />
                          <label htmlFor="default-checkbox" className="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300">Confirm apartment id</label>
                        </div>
                        <a className="text-gray-500" href="#!">Tutto apposto?</a>
                      </div>
                      { /** 
                    <div className="flex items-center justify-between pb-6">
                      <p className="mb-0 mr-2">Don't have an account?</p>
                      <button
                        type="button"
                        className="inline-block px-6 py-2 border-2 border-red-600 text-red-600 font-medium text-xs leading-tight uppercase rounded hover:bg-black hover:bg-opacity-5 focus:outline-none focus:ring-0 transition duration-150 ease-in-out"
                        data-mdb-ripple="true"
                        data-mdb-ripple-color="light"
                      >
                        Danger
                      </button>
                    </div>
                  */ }

                    </form>
                  </div>
                </div>
                <div
                  className="lg:w-6/12 flex items-center lg:rounded-r-lg rounded-b-lg lg:rounded-bl-none"
                >
                  <div className="text-black px-4 py-6 md:p-12 md:mx-6">
                    <h4 className="text-xl font-semibold mb-6">We are more than just a bin, let me explain y.</h4>
                    <p className="text-sm">
                      Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                      quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                      consequat.

                      Spiega che roba è.

                      Bidone fantastico bellissimo me lo sposo guarda eccomi ciao.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}


export default Login


